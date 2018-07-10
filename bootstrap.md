# Create initial superuser
```bash
echo "from authentication_service.models import CoreUser; CoreUser.objects.create_superuser(username='cobusc', email='cobusc@praekeltconsulting.com', password='something', birth_date='1979-01-13')" | python manage.py shell
```
# Create RSA key
```
python manage.py creatersakey
```

Create a client for the Management Portal
Client Type: public
Response Type: id_token token (Implicit Flow)
Redirect URIs: https://portal.gehosting.org/#/oidc/callback?
JWT Alg: RS256
Require Consent: Yes
Reuse Consent: Yes
Website URL: https://portal.gehosting.org/
Post Logout Redirect URIs: https://portal.gehosting.org/
```

On Access Control, run `python bootstrap_management_portal.py 1`, where `1` is the ID of the client created for the Management Portal.
> Note that this script will create the top level domain and the management portal site. It is idempotent.

On Access Control, run `python bootstrap_tech_admin_user.py 609867d6-68c1-11e8-b5b6-0242ac110004`, where `609867d6-68c1-11e8-b5b6-0242ac110004` is the ID of the user that needs to be granted the tech admin role.
> Note that this script will create the top level domain, the tech admin role, the domain role and the user domain role. It is idempotent.

> Note: After mods the following can be done: `python manage.py createsuperuser --noinput --user testing2 --email testing2@example.com --birth_date 1979-01-01`. The user will need to do a password reset via email.

