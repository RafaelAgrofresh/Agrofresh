from .structs import DataStruct


def struct_fields(request):
    context = {
        "fields": DataStruct.get_fields_lut(),
    }
    return context