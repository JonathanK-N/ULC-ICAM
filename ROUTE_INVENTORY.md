# Inventaire des routes

Inventaire statique de la branche ; les permissions doivent aussi être vérifiées par parcours dynamiques.

| Route | Méthodes | Source | Fonction |
|---|---|---|---|
| / | GET | app.py:729 | index |
| /admin/add_course | GET, POST | app.py:1552 | admin_add_course |
| /admin/add_student | GET, POST | app.py:1086 | add_student |
| /admin/add_teacher | GET, POST | app.py:1124 | add_teacher |
| /admin/assign_teacher/<int:course_id> | GET, POST | app.py:1578 | assign_teacher_to_course |
| /admin/assignments | GET | app.py:1907 | admin_assignments |
| /admin/check_all_plagiarism | POST | app.py:3287 | check_all_plagiarism |
| /admin/config/<config_type> | GET, POST | app.py:1508 | manage_config |
| /admin/courses | GET | app.py:1546 | admin_courses_view |
| /admin/delete_user/<username> | POST | app.py:1276 | delete_user |
| /admin/download_backup | GET | app.py:3250 | download_backup |
| /admin/edit_user/<username> | GET, POST | app.py:1435 | edit_user |
| /admin/export_all_data | GET | app.py:3183 | export_all_data |
| /admin/generate_full_report | GET | app.py:3206 | generate_full_report |
| /admin/import_csv | GET, POST | app.py:1162 | import_csv |
| /admin/recheck_plagiarism/<int:submission_id> | POST | app.py:3317 | recheck_plagiarism |
| /admin/seed | GET, POST | app.py:3407 | admin_seed |
| /admin/students | GET | app.py:1930 | admin_students |
| /admin/submissions | GET | app.py:1913 | admin_submissions |
| /admin/system_config | GET | app.py:1502 | system_config_view |
| /admin/system_report | GET | app.py:3164 | system_report |
| /admin/teachers | GET | app.py:1937 | admin_teachers |
| /admin/unassign_teacher/<int:course_id>/<teacher_username> | POST | app.py:1630 | unassign_teacher_from_course |
| /admin/upload_photo/<username> | POST | app.py:1408 | upload_photo |
| /admin/user_profile/<username> | GET | app.py:1396 | user_profile |
| /admin/users | GET | app.py:1080 | admin_users |
| /change_password | GET, POST | app.py:1287 | change_password |
| /dashboard | GET | app.py:842 | dashboard |
| /download_assignment_file/<filename> | GET | app.py:2048 | download_assignment_file |
| /download_chapter_document/<filename> | GET | app.py:1891 | download_chapter_document |
| /download_correction/<filename> | GET | app.py:2120 | download_correction_file |
| /download_file/<filename> | GET | app.py:2070 | download_file |
| /download_syllabus/<int:course_id>/<filename> | GET | app.py:1713 | download_syllabus |
| /health | GET | app.py:723 | health_check |
| /login | GET | app.py:743 | login |
| /login/admin | GET, POST | app.py:815 | admin_login |
| /login/student | GET, POST | app.py:747 | student_login |
| /login/teacher | GET, POST | app.py:781 | teacher_login |
| /logout | GET | app.py:837 | logout |
| /manifest.json | GET | app.py:304 | web_manifest |
| /offline.html | GET | app.py:2066 | offline |
| /student/course/<int:course_id> | GET | app.py:2985 | student_course_detail |
| /student/courses | GET | app.py:2975 | student_courses |
| /student/join_group/<int:assignment_id> | GET, POST | app.py:2812 | join_group |
| /student/my_grades | GET | app.py:2929 | student_grades |
| /submit/<int:assignment_id> | GET, POST | app.py:914 | submit_assignment |
| /sw.js | GET | app.py:323 | service_worker |
| /teacher/add_chapter/<int:course_id> | POST | app.py:1743 | add_chapter |
| /teacher/add_exercise/<int:course_id>/<int:chapter_id> | POST | app.py:1833 | add_exercise |
| /teacher/assignment_results/<int:assignment_id> | GET | app.py:2152 | assignment_results |
| /teacher/assignment_submissions/<int:assignment_id> | GET | app.py:2910 | assignment_submissions |
| /teacher/assignments | GET | app.py:1944 | teacher_assignments |
| /teacher/chapter/<int:course_id>/<int:chapter_id> | GET | app.py:1793 | chapter_detail |
| /teacher/course/<int:course_id> | GET | app.py:1318 | course_detail |
| /teacher/course_content/<int:course_id> | GET | app.py:1661 | course_content_view |
| /teacher/courses | GET | app.py:1657 | teacher_courses |
| /teacher/create_assignment | GET, POST | app.py:1952 | create_assignment |
| /teacher/download_all_submissions/<int:assignment_id> | GET | app.py:3069 | download_all_submissions |
| /teacher/enroll_student/<int:course_id>/<username> | POST | app.py:1351 | enroll_student |
| /teacher/export_course_data/<int:course_id> | GET | app.py:3139 | export_course_data |
| /teacher/generate_report/<int:assignment_id> | GET | app.py:3116 | generate_assignment_report |
| /teacher/grade_submission/<int:submission_id> | GET, POST | app.py:2182 | grade_submission |
| /teacher/manage_groups/<int:assignment_id> | GET | app.py:2860 | manage_groups |
| /teacher/my_assigned_courses | GET | app.py:1643 | teacher_assigned_courses |
| /teacher/publish_results/<int:assignment_id> | POST | app.py:3004 | publish_results |
| /teacher/publish_submissions/<int:assignment_id> | POST | app.py:2237 | publish_submissions |
| /teacher/students | GET | app.py:2883 | teacher_students |
| /teacher/submissions | GET | app.py:2875 | teacher_submissions |
| /teacher/unenroll_student/<int:course_id>/<username> | POST | app.py:1375 | unenroll_student |
| /teacher/unpublish_results/<int:assignment_id> | POST | app.py:3026 | unpublish_results |
| /teacher/unpublish_submissions/<int:assignment_id> | POST | app.py:2258 | unpublish_submissions |
| /teacher/update_chapter/<int:course_id>/<int:chapter_id> | POST | app.py:1814 | update_chapter |
| /teacher/update_course_description/<int:course_id> | POST | app.py:1727 | update_course_description |
| /teacher/upload_chapter_document/<int:course_id>/<int:chapter_id> | POST | app.py:1855 | upload_chapter_document |
| /teacher/upload_syllabus/<int:course_id> | POST | app.py:1682 | upload_syllabus |
| /test_submit | POST | execution_routes.py:9 | test_submit |
| /upload_analysis_files/<int:assignment_id> | POST | app.py:3351 | upload_analysis_files |
