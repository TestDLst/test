import re
import string


class Encoder:
    def __init__(self):
        pass

    @staticmethod
    def double_url_encode(payload):
        retVal = payload

        if payload:
            retVal = ""
            i = 0

            while i < len(payload):
                if payload[i] == '%' and (i < len(payload) - 2) and payload[
                                                                    i + 1:i + 2] in string.hexdigits and payload[
                                                                                                         i + 2:i + 3] in string.hexdigits:
                    retVal += '%%25%s' % payload[i + 1:i + 3]
                    i += 3
                else:
                    retVal += '%%25%.2X' % ord(payload[i])
                    i += 1

        return retVal

    @staticmethod
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

    @staticmethod
    def html_encode(payload):
        return re.sub(r"[^\w]", lambda match: "&#%d;" % ord(match.group(0)), payload) if payload else payload