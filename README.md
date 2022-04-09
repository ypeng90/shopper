# Single-page Web Application for Local Shopping

## Main Features

- A flexible plug-in architecture to collect and present product inventory info.
- An account management system using self-implemented and fully customizable Captcha.
- Security procedures to manage authorization and prevent malicious attacks.

## Architecture

### Use Case Diagram

![Use Case Diagram](./docs/use_case_diagram.png?raw=true)

### Component Diagram

![Component Diagram](./docs/component_diagram.png?raw=true)

### Class Diagram

#### Account

![Class Diagram Account](./docs/class_diagram_account.png?raw=true)

#### Shopper

![Class Diagram Shopper](./docs/class_diagram_shopper.png?raw=true)

## Security Procedures

- Fully customizable Captcha can make CAPTCHA recognition by robots significantly more challenging.
- Users are uniquely identified by cryptographically-secure random userids. All passwords are hashed (SHA256) with cryptographically-secure random salt.
- Access control is implemented with JWT token based authentication and authorization mechanism.
- Enforced input sanitization can help to prevent XSS and SQL injection attacks.
- Enforcd usage of prepared statement for database query can help to prevent SQL injection attacks.
- Enforced usage of CSRF token can help to prevent CSRF attacks.
