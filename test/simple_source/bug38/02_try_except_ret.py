# The bug in 3.8 was handling the returns in the before and in the except blocks.
# This kind of code generation starts in 3.8
# The return value may appear on either side of a POP_BLOCK and
# the try_except will be missing not have specific COME_FROMs since
# there are returns
def set_reg(name, winreg):
    try:
        value = winreg(name)
        return value
    except RuntimeError:
        return None


def get_reg(name, winreg):
    try:
        winreg(name)
        return True
    except RuntimeError:
        return winreg


def nested_try_finally(d):
    try:

        try:
            x = 1
        except:  # noqa
            return d()
    finally:
        x = 2
    return x


def nested_try_finally_with_stmt1(fn, x, *args, **kwargs):
    try:
        try:
            x += 1
        except Exception:
            x += 2
            return fn(args, sn=5, **kwargs)
    finally:
        x += 2
    return fn(args, sn=6, **kwargs) + x


def nested_try_finally_with_stmt2(fn, x, *args, **kwargs):
    try:
        try:
            x += 1
        except:  # noqa
            x += 2
            return fn(args, sn=5, **kwargs)
    finally:
        x += 2
    return fn(args, sn=6, **kwargs) + x


def try_except_as(fn, x, *args, **kwargs):
    try:
        x += 1
    except Exception as e:
        x += 2
        return fn(args, sn=e, **kwargs)
