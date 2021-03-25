# Website-with-vulnerabilities
A website with vulnerabilities for a cyber security course. The flaws are mentioned in an essay along with some proposed fixes.

## Website usage
The website follows the traditional structure of a blog app. You can see all the posts created by all users at the home page. You must signup/login in order to create posts. You can also leave comments to any post if you are logged in. Also you have the option to delete your posts, comments or even your account.

## Essay
### Setup:
1. Clone the respository linked above.
2. Execute the necessary migrations with ('py manage.py makemigrations' and 'py manage.py migrate' or equivalents in your OS).
3. Run the server with 'py manage.py runserver'.
Note: If you are not sure how to use the app, the GitHub repository has a short description in the readme.md file.

### FLAW 1: Insecure transport
https://github.com/JustLearningThings/Website-with-vulnerabilities/blob/main/cybsecflaws/settings.py#L139 - settings.py (line 139 - 144)
It is well-known that every software that uses Internet must use HTTPS over HTTP. It is crucial for any application that sends data back and forth over the Internet, because the data sent should be encrypted.
According to OWASP it is not enough the enable SSL and gives a list of reasons for that. Firstly, a user may enter the URL manually, switching between HTTP and HTTPS. Then, an attacker may be able to send a user to an insecure URL, for example by performing a man-in-the-middle attack. Also, a developer may accidentally create a link to an insecure area of a website. The most important parts to secure are the authentication along with any forms or pages that get or send sensitive data.
This flaw may be interpreted either as sensitive data exposure or security misconfiguration.

Not enforcing HTTPS in our application results in sending a user’s password in plaintext to the server. This can happen at the login and signup routes. This is a serious security vulnerability.
Django has an article about deploying with SSL/HTTPS where, among other things, they mention using SECURE_SSL_REDIRECT=True to redirect HTTP requests to HTTPS and also to use cookies with the secure flag enabled. Follow the link above for a proper configuration that should've been done.

Sources: https://owasp.org/www-community/vulnerabilities/Insecure_Transport, https://docs.djangoproject.com/en/3.1/topics/security/#ssl-https


### FLAW 2: Lack of rate limiting and pagination
https://github.com/JustLearningThings/Website-with-vulnerabilities/blob/main/blog/views.py#L12

In our Django app there are numerous places where the views request all the available objects (filtered or not) from the database and then send them to templates for rendering. The number of these objects may be too high, resulting in a DOS. Even the filtered queries should be considered potential DOS vectors. One such a place is in the index view (link above points to this view, but other views have this problem too). There, all the posts are fetched from the database, without limits or any further pagination, which may slow down the server.

A proper solution would be to implement pagination on every resource that fetches data from the database not based on primary keys of the desired objects. Regarding rate limiting, there are libraries or frameworks that offer this kind of functionality. For example, django-ratelimit provides decorators for views, or Django REST Framework has rate limiting. Also, some web servers (like NGINX) have load balancers and rate limiters.

Sources: https://curity.io/resources/learn/owasp-to-ten/#4-lack-of-resources--rate-limiting (they cite OWASP)

### FLAW 3: Brute-force-vulnerable authentication
https://github.com/JustLearningThings/Website-with-vulnerabilities/blob/main/blog/views.py#L162 - for testing the solution

In their article on security, Django developers mention that their framework does not throttle requests to authenticate a user. This means that a brute-force attack is possible and any user with a weak password may become affected.

In the same article they recommend deploying a Django plugin or Web server module to throttle requests. Actually, throttling can be handled manually by not allowing a user to enter credentials for a given time if it was wrong (similar to how smartphones handle passwords) or a similar technique, but using the above methods is better, because they are already tested. Also, using a CAPTCHA is recommended to avoid bots.
The link above points to how rate-limit may have been added to our app.

Sources: https://docs.djangoproject.com/en/3.1/topics/security/#additional-security-topics,
https://stackoverflow.com/questions/11477067/throttling-brute-force-login-attacks-in-django (some solutions mentioned on stackoverflow)

### FLAW 4: Broken Authorization
https://github.com/JustLearningThings/Website-with-vulnerabilities/blob/main/blog/views.py#L80
In our Django app in some place authorization is broken. One of the most dangerous is profileDeleteView for obvious reasons. Here, the view deletes an account based on the user id provided in the URL. It doesn’t check the user session to be sure that the account to be deleted is the one from the user that requested its deletion.
The easiest way to delete an account with this vulnerability in our Django app is to create an account, go to the profile page and change the URL of the form to contain the desired user’s id (using Dev Tools). When clicking the button to delete the account that has just been created, the targeted account is actually removed. This exploit is performed easier than fetching a POST to this URL because the app expects a CSRF token from the form.

To solve this the view must check request.user to equal the user’s id from the URL (line 84 in views.py). Also, the views that require personal information or that change user data should have login_required decorator.

### Flaw 5: Security misconfiguration
https://github.com/JustLearningThings/Website-with-vulnerabilities/blob/main/cybsecflaws/settings.py#L28,
The secret key used by Django is in plain sight. It should be taken from an environment variable as shown in the commented code from the link above.
Another problem is that the ALLOWED_HOSTS is set to an empty list. It should contain a list of all the hosts our application is expecting to serve. Otherwise, if the site went to production, it would’ve been prone to Host header attacks where a fake Host value can be used for Cross-Site Request Forgery, cache poisoning attacks, and poisoning links in emails.

Sources: https://docs.djangoproject.com/en/3.1/topics/security/#host-header-validation

### Flaw 6: Data upload related issues
https://github.com/JustLearningThings/Website-with-vulnerabilities/blob/main/cybsecflaws/settings.py#L148
Django’s docs advise to limit the size of uploaded files and other data in the configurations of the web server to a reasonable size. The default size of the request body is set to be 2.5 MB. This can be handled with the FILE_UPLOAD_MAX_MEMORY_SIZE and DATA_UPLOAD_MAX_MEMORY_SIZE. Moreover, we can limit the maximum number of parameters received via GET or POST requests (defaults to 1000). The docs mention that the number of request parameters is correlated to the amount of time needed to process and populate the GET and POST dictionaries. They also mention that large requests may result in a DOS.
As of our application’s requirements, having a maximum of 1000 request parameters is too much. If a user intentionally loads the request with a lot of parameters and sends many repeated requests (again, we don’t have any load balancers or rate limiters) it gets faster to perform a DOS. But we leave the upload max size to the default, because we have the functionality to upload images, which are generally not bigger than 2.5 MB.
Another important thing that the Django documentation mentions is that a user may upload specially crafted files, like an HTML file with PNG headers, which will be considered as a PNG file by our application. This may be considered as a flaw classified by OWASP as Using Components with Known Vulnerabilities, because the Django’s documentation says that the cause of this problem is the Pillow library that they use for image processing. It is recommended to disable any handlers that execute static files as code and to serve user uploaded files from a top-level domain in our app. But the best way to avoid this is to actually serve those files from a cloud server or a CDN.
Sources: https://docs.djangoproject.com/en/3.1/topics/security/#user-uploaded-content-security, https://docs.djangoproject.com/en/3.1/ref/settings/#std:setting-FILE_UPLOAD_MAX_MEMORY_SIZE, https://docs.djangoproject.com/en/3.1/ref/settings/#std:setting-DATA_UPLOAD_MAX_MEMORY_SIZE

### Flaw 7: Weak passwords
https://github.com/JustLearningThings/Website-with-vulnerabilities/blob/main/blog/forms.py#L13 (also check lines 7 and 8 for the validator code)
As mentioned in the third flaw, our users can have weak passwords. We don’t measure the strength of the user’s password at form input level. We should have a regular expression that tests its strength. Django has built-in validation functionality to cope with this problem.

Sources: https://docs.djangoproject.com/en/3.1/ref/forms/validation/ , https://stackoverflow.com/questions/16965953/regular-expressions-for-username-and-password
