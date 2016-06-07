def has_root_label(dn):
    '''Check domain name has trailing '.' root label.'''
    if dn.endswith('.'):
        return True
    return False


def add_root_label(name):
    '''Return domain name with trailing '.' root label.'''
    if not has_root_label(name):
        return name + '.'
    return name


