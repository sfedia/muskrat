#!/usr/bin/python3
from collections import namedtuple

object_model = namedtuple('muskrat_object', 'type content connected')


def scan_row(object_row, sample):
    if len(sample) != len(object_row):
        return False

    for j, obj in enumerate(object_row):
        if sample[j].type is not None:
            if sample[j].type != obj.pattern.object_type:
                return False

        if sample[j].content is not None:
            if sample[j].content != obj.content:
                return False

        if sample[j].connected is not None:
            if not scan_row(obj.connected_objects, sample[j].connected):
                return False

    return True
