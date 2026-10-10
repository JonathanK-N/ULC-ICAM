(() => {
  const status = document.getElementById('push-status');
  const csrf = document.querySelector('meta[name="csrf-token"]')?.content;
  const post = async (url, data) => {
    const response = await fetch(url, { method: 'POST', credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf }, body: JSON.stringify(data) });
    if (!response.ok) throw new Error('La modification n’a pas pu être enregistrée. Réessayez.');
    return response.json();
  };
  document.getElementById('enable-push').addEventListener('click', async () => {
    try {
      if (!('serviceWorker' in navigator) || !('PushManager' in window)) throw new Error('Ce navigateur ne prend pas en charge les notifications.');
      const config = await (await fetch('/api/notifications/push-config')).json();
      if (!config.enabled) throw new Error('Les notifications ne sont pas disponibles.');
      if (await Notification.requestPermission() !== 'granted') throw new Error('Autorisation refusée. Vous pouvez la modifier dans les réglages du navigateur.');
      await navigator.serviceWorker.register('/sw.js');
      const registration = await navigator.serviceWorker.ready;
      const padded = config.public_key.replace(/-/g, '+').replace(/_/g, '/') + '='.repeat((4 - config.public_key.length % 4) % 4);
      const key = Uint8Array.from(atob(padded), c => c.charCodeAt(0));
      const subscription = await registration.pushManager.getSubscription() || await registration.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: key });
      await post('/api/notifications/subscriptions', subscription.toJSON());
      status.textContent = 'Notifications activées sur cet appareil.';
    } catch (error) { status.textContent = error.message; }
  });
  document.getElementById('disable-push').addEventListener('click', async () => {
    try {
      const registration = await navigator.serviceWorker.getRegistration('/');
      const subscription = await registration?.pushManager.getSubscription();
      if (subscription) {
        const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(subscription.endpoint));
        const id = Array.from(new Uint8Array(digest), b => b.toString(16).padStart(2, '0')).join('');
        await post('/api/notifications/subscriptions/remove', { id });
        await subscription.unsubscribe();
      }
      status.textContent = 'Notifications désactivées sur cet appareil.';
    } catch (error) { status.textContent = error.message; }
  });
})();
