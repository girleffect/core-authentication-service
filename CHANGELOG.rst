Changelog
=========

next
----
- Generate endpoints for invitation redirect url addition
- Update registration success to display unique template if invitation had a redirect url
- Invitation email now includes expiry date

1.4.0
-----
- Added test language: en-you
- Added `CORS_ORIGIN_WHITELIST` environment variable setting.

1.3.0
-----
- GEINFRA-60
- GEINFRA-118
- GEINFRA-119
- GEINFRA-124
- GEINFRA-138
- GEINFRA-154
- GEINFRA-236
- GEINFRA-237
- GEINFRA-239
- GEINFRA-245
- GEINFRA-246
- GEINFRA-248
- GEINFRA-249
- GEINFRA-251


1.2.2
-----
Bugfix: Correct format of datetime argument passed to the deleted_user_update() call of the User Data Store.

1.2.1
-----
#. feature/GE-1100: Prevent users younger than 13 from registering an account or reducing age via edit profile
#. Reworked themes, reduce templates, update styles
#. feature/GE-1128: Translation tag updates, reduce HTML and CSS elements in blocktrans blocks and trans tags. Reworked some python strings to not include none string characters where possible.
#. feature/GE-1086: Registration security questions can be preselected via url query parameter.
#. feature/GE-1066: Registration split into multi page wizard.
#. Renamed `OrginasationalUnit` to `Organisation`
#. feature/GEINFRA-62: Edit profile now correctly updates user age.
#. feature/GEINFRA-59: Update default admin user creation to sport more fields.
#. feature/GEINFRA-58: Updates to security question model unique constraints.
#. feature/GEINFRA-95: Revert some template regressions from registration wizard updates.
#. feature/GEINFRA-66: Invitation System: send invitation mail API endpoint.
#. feature/GEINFRA-78: Setup new S3 storage backend and CloudFront CDN for statics and media.
#. feature/GEINFRA-67: Registration updated to make use of incitation urls.
#. feature/GEINFRA-137: Refactor registration login code to not prematurely clear session.
#. Various tweaks, fixes and updates.

1.2.0
-----
#. Various bugfixes from errors picked up on QA
#. Themes updated
#. feature/GE-1120: Account deletion error message fix
#. feature/GE-1115: Keep theme when redirecting
#. feature/GE-1116: Changed admin template to make use of auth service base
#. feature/GE-1117: 2FA disabled (for now)
#. feature/GE-1085: Password reset for unmigrated users

1.1.1
-----
#. Fixed bug that made the createsuperuser management command unusable.
#. Added management command to load country data.

1.1.0
-----
- Added healthcheck API end-point.

1.0.0
-----
- Initial release

