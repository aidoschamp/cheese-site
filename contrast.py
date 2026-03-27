def textColour(bgColour):
    r = int(bgColour[1:3], 16)
    g = int(bgColour[3:5], 16)
    b = int(bgColour[5:7], 16)

    r_srgb = r / 255.0
    g_srgb = g / 255.0
    b_srgb = b / 255.0

    r_linear = r_srgb / 12.92 if r_srgb <= 0.03928 else ((r_srgb + 0.055) / 1.055) ** 2.4
    g_linear = g_srgb / 12.92 if g_srgb <= 0.03928 else ((g_srgb + 0.055) / 1.055) ** 2.4
    b_linear = b_srgb / 12.92 if b_srgb <= 0.03928 else ((b_srgb + 0.055) / 1.055) ** 2.4

    L = 0.2126 * r_linear + 0.7152 * g_linear + 0.0722 * b_linear

    if L > 0.179:
        return"#000000"
    else:
        return "#ffffff"