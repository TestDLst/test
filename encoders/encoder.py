import re
import string
from urllib.parse import quote_plus


def no_encode(payload):
    return payload


def url_encode(payload):
    return quote_plus(payload)


def double_url_encode(payload):
    return quote_plus(quote_plus(payload))


def unicode_encode(payload):
    retVal = payload

    if payload:
        retVal = ""
        i = 0

        while i < len(payload):
            if payload[i] == '%' and (i < len(payload) - 2) and payload[
                                                                i + 1:i + 2] in string.hexdigits and payload[
                                                                                                     i + 2:i + 3] in string.hexdigits:
                retVal += "%%u00%s" % payload[i + 1:i + 3]
                i += 3
            else:
                retVal += '%%u%.4X' % ord(payload[i])
                i += 1

    return retVal


def decimal_html_encode(payload):
    return re.sub('.', lambda match: "&#{:0>7}".format(ord(match.group(0))), payload)


def hexadecimal_html_encode(payload):
    return re.sub('.', lambda match: "&#{}".format(hex(ord(match.group(0)))[1:]), payload)


# if __name__ == '__main__':
#     with open('../payloads/fuzzing/common.txt', 'w') as f:
#         f.writelines('\n'.join(string.punctuation))