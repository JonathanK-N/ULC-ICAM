# Inventaire des routes

Inventaire statique des contrôleurs Flask et Blueprints. Les autorisations sont aussi vérifiées par tests de parcours. Les alias de compatibilité ne créent pas de nouveaux accès.

| Route | Méthodes | Source | Fonction |
|---|---|---|---|
| / | GET | core_routes.py:35 | index |
| /admin/add_course | GET, POST | courses_routes.py:73 | admin_add_course |
| /admin/add_student | GET, POST | admin_routes.py:14 | add_student |
| /admin/add_teacher | GET, POST | admin_routes.py:32 | add_teacher |
| /admin/assign_teacher/<int:course_id> | GET, POST | courses_routes.py:87 | assign_teacher_to_course |
| /admin/assignments | GET | assignments_routes.py:100 | admin_assignments |
| /admin/check_all_plagiarism | POST | grading_routes.py:182 | check_all_plagiarism |
| /admin/config/<config_type> | GET, POST | admin_routes.py:192 | manage_config |
| /admin/courses | GET | courses_routes.py:67 | admin_courses_view |
| /admin/delete_user/<username> | POST | admin_routes.py:112 | delete_user |
| /admin/download_backup | GET | reports_routes.py:129 | download_backup |
| /admin/edit_user/<username> | GET, POST | admin_routes.py:162 | edit_user |
| /admin/export_all_data | GET | reports_routes.py:89 | export_all_data |
| /admin/generate_full_report | GET | reports_routes.py:100 | generate_full_report |
| /admin/import_csv | GET, POST | admin_routes.py:50 | import_csv |
| /admin/recheck_plagiarism/<int:submission_id> | POST | grading_routes.py:209 | recheck_plagiarism |
| /admin/seed | GET, POST | admin_routes.py:233 | admin_seed |
| /admin/students | GET | admin_routes.py:219 | admin_students |
| /admin/submissions | GET | assignments_routes.py:106 | admin_submissions |
| /admin/system_config | GET | admin_routes.py:186 | system_config_view |
| /admin/system_report | GET | reports_routes.py:81 | system_report |
| /admin/teachers | GET | admin_routes.py:226 | admin_teachers |
| /admin/unassign_teacher/<int:course_id>/<teacher_username> | POST | courses_routes.py:124 | unassign_teacher_from_course |
| /admin/upload_photo/<username> | POST | admin_routes.py:140 | upload_photo |
| /admin/user_profile/<username> | GET | admin_routes.py:130 | user_profile |
| /admin/users | GET | admin_routes.py:8 | admin_users |
| /change_password | GET, POST | auth_routes.py:136 | change_password |
| /dashboard | GET | core_routes.py:43 | dashboard |
| /download_assignment_file/<filename> | GET | assignments_routes.py:183 | download_assignment_file |
| /download_chapter_document/<filename> | GET | courses_routes.py:320 | download_chapter_document |
| /download_correction/<filename> | GET | grading_routes.py:8 | download_correction_file |
| /download_file/<filename> | GET | assignments_routes.py:197 | download_file |
| /download_syllabus/<int:course_id>/<filename> | GET | courses_routes.py:191 | download_syllabus |
| /health | GET | core_routes.py:30 | health_check |
| /login | GET | auth_routes.py:12 | login |
| /login/admin | GET, POST | auth_routes.py:99 | admin_login |
| /login/student | GET, POST | auth_routes.py:21 | student_login |
| /login/teacher | GET, POST | auth_routes.py:60 | teacher_login |
| /logout | GET | auth_routes.py:126 | logout |
| /manifest.json | GET | core_routes.py:8 | web_manifest |
| /offline.html | GET | core_routes.py:80 | offline |
| /reports/generated/<identifier> | GET | reports_routes.py:29 | generated_report |
| /student/course/<int:course_id> | GET | courses_routes.py:341 | student_course_detail |
| /student/courses | GET | courses_routes.py:333 | student_courses |
| /student/join_group/<int:assignment_id> | GET, POST | groups_routes.py:8 | join_group |
| /student/my_grades | GET | grading_routes.py:119 | student_grades |
| /submit/<int:assignment_id> | GET, POST | assignments_routes.py:9 | submit_assignment |
| /sw.js | GET | core_routes.py:19 | service_worker |
| /teacher/add_chapter/<int:course_id> | POST | courses_routes.py:218 | add_chapter |
| /teacher/add_exercise/<int:course_id>/<int:chapter_id> | POST | courses_routes.py:279 | add_exercise |
| /teacher/assignment_results/<int:assignment_id> | GET | grading_routes.py:33 | assignment_results |
| /teacher/assignment_submissions/<int:assignment_id> | GET | assignments_routes.py:236 | assignment_submissions |
| /teacher/assignments | GET | assignments_routes.py:114 | teacher_assignments |
| /teacher/chapter/<int:course_id>/<int:chapter_id> | GET | courses_routes.py:247 | chapter_detail |
| /teacher/course/<int:course_id> | GET | courses_routes.py:8 | course_detail |
| /teacher/course_content/<int:course_id> | GET | courses_routes.py:149 | course_content_view |
| /teacher/courses | GET | courses_routes.py:145 | teacher_courses |
| /teacher/create_assignment | GET, POST | assignments_routes.py:121 | create_assignment |
| /teacher/download_all_submissions/<int:assignment_id> | GET | assignments_routes.py:248 | download_all_submissions |
| /teacher/enroll_student/<int:course_id>/<username> | POST | courses_routes.py:30 | enroll_student |
| /teacher/export_course_data/<int:course_id> | GET | reports_routes.py:63 | export_course_data |
| /teacher/generate_report/<int:assignment_id> | GET | reports_routes.py:45 | generate_assignment_report |
| /teacher/generate_report_async/<int:assignment_id> | POST | reports_routes.py:8 | queue_assignment_report |
| /teacher/grade_submission/<int:submission_id> | GET, POST | grading_routes.py:53 | grade_submission |
| /teacher/manage_groups/<int:assignment_id> | GET | groups_routes.py:52 | manage_groups |
| /teacher/my_assigned_courses | GET | courses_routes.py:135 | teacher_assigned_courses |
| /teacher/publish_results/<int:assignment_id> | POST | grading_routes.py:150 | publish_results |
| /teacher/publish_submissions/<int:assignment_id> | POST | grading_routes.py:91 | publish_submissions |
| /teacher/students | GET | teachers_routes.py:8 | teacher_students |
| /teacher/submissions | GET | assignments_routes.py:229 | teacher_submissions |
| /teacher/unenroll_student/<int:course_id>/<username> | POST | courses_routes.py:50 | unenroll_student |
| /teacher/unpublish_results/<int:assignment_id> | POST | grading_routes.py:167 | unpublish_results |
| /teacher/unpublish_submissions/<int:assignment_id> | POST | grading_routes.py:106 | unpublish_submissions |
| /teacher/update_chapter/<int:course_id>/<int:chapter_id> | POST | courses_routes.py:263 | update_chapter |
| /teacher/update_course_description/<int:course_id> | POST | courses_routes.py:205 | update_course_description |
| /teacher/upload_chapter_document/<int:course_id>/<int:chapter_id> | POST | courses_routes.py:294 | upload_chapter_document |
| /teacher/upload_syllabus/<int:course_id> | POST | courses_routes.py:166 | upload_syllabus |
| /test_submit | POST | execution_routes.py:9 | test_submit |
| /upload_analysis_files/<int:assignment_id> | POST | assignments_routes.py:285 | upload_analysis_files |
