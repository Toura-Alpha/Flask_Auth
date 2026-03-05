# TODO: Security Implementation Checklist

## Priority 1: Critical

- [x] 1.1 Move SECRET_KEY to environment variable
- [x] 1.2 Move Google OAuth credentials to environment variables
- [x] 1.3 Add Flask-WTF for CSRF protection

## Priority 2: High

- [x] 2.1 Add password strength validation
- [ ] 2.2 Add rate limiting for login attempts

## Priority 3: Medium

- [x] 3.1 Configure secure session cookies
- [x] 3.2 Use absolute path for database
- [ ] 3.3 Add account lockout after failed attempts
- [ ] 3.4 Implement proper error messages

## Additional Features Implemented

- [x] Separate register.html page
- [x] Navigation bar with dynamic links
- [x] Modern styling with CSS in base.html
- [x] Login/Register page separation

---

## Status: In Progress

**Completed: Priority 1 (Critical), Password validation, Session security, Database path, Navigation & Styling**
**Next: Rate limiting, account lockout**
