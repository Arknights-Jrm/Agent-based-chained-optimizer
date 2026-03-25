def external_simulation_interface(params):
    patch_length, patch_width, substrate_height = params
    vswr = 1.0 + (patch_length-0.05)**2 + (patch_width-0.05)**2 + (substrate_height-0.005)**2
    return vswr  # 