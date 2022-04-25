# Django based Local Shopping Planning Web Service

## Main Features

- Developed a web service with Python, Django, MySQL, Redis, Vue.js, and Leaflet.
- Implemented a MVC backend with Django, GeoDjango, MySQL, and JWT, and an asynchronous task queue with Celery, RabbitMQ, and Redis.
- Developed an AJAX based frontend with interactive map using Vue.js, GeoJSON, and Leaflet.
- Implemented a fully customizable Captcha with Pillow for user authentication.
- Developed a web scraper with Requests and urllib3 to collect local inventory information.
- Implemented security procedures to manage authorization and prevent malicious attacks.

## Architecture

### Use Case Diagram

![Use Case Diagram](./docs/use_case_diagram.png?raw=true)

### Component Diagram

![Component Diagram](./docs/component_diagram.png?raw=true)

### Class Diagram

#### Account

![Class Diagram Account](./docs/class_diagram_account.png?raw=true)

#### Product

![Class Diagram Product](./docs/class_diagram_product.png?raw=true)

## Security Procedures

- Fully customizable Captcha can make CAPTCHA recognition by robots significantly more challenging.
- Users are uniquely identified by cryptographically-secure random userids. All passwords are hashed (SHA256) with cryptographically-secure random salt.
- Access control is implemented with JWT token based authentication and authorization mechanism.
- Enforced input sanitization can help to prevent XSS and SQL injection attacks.
- Enforcd usage of prepared statement for database query can help to prevent SQL injection attacks.
- Enforced usage of CSRF token can help to prevent CSRF attacks.
