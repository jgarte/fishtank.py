"""
fishtank.styles
---------------
author: bczsalba


Module containing UI style initiators.
"""


from pytermgui import color, bold, highlight, set_style


def get_depth(level: int, colors: list[int]) -> int:
    """ Return color based on depth from colors """

    return colors[min(level, len(colors) - 1)]


def default() -> None:
    """ Default color style """

    depth_colors = [60, 67, 74, 81]

    set_style(
        "container_border",
        lambda depth, item: bold(color(item, get_depth(depth, depth_colors))),
    )

    # set_style('container_corner_chars', lambda: "..''")
    set_style("label_value", lambda depth, item: bold(color(item, 223)))
    set_style("prompt_label", lambda depth, item: color(item, 248))
    set_style("prompt_value", lambda depth, item: color(item, 223))
    set_style(
        "inputfield_value",
        lambda depth, item: color(item, get_depth(depth, depth_colors)),
    )
    set_style(
        "inputfield_highlight",
        lambda depth, item: highlight(item, get_depth(depth, depth_colors)),
    )
    set_style(
        "prompt_short_highlight", lambda depth, item: highlight(item, 72)
    )
    set_style("prompt_long_highlight", lambda depth, item: highlight(item, 72))
    set_style("prompt_delimiter_chars", lambda: "<>")
