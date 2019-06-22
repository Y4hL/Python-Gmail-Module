class GmailException(RuntimeError):
    """There was an ambiguous exception that occurred while handling your
    request."""

class AuthenticationError(GmailException):
    """Gmail Authentication failed."""

class MailboxExists(GmailException):
    """Mailbox already exists"""
