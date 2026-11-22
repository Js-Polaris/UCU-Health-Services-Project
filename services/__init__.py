"""Service layer.

Services own the transaction: they call repositories, then commit once on
success and roll back once on failure. Views never commit, roll back or write
SQL -- they only call these classes and display the result or the exception.
"""
