import wagtail.admin.rich_text.editors.draftail.features as draftail_features
from wagtail.admin.rich_text.converters.html_to_contentstate import (
    InlineStyleElementHandler,
)
from wagtail import hooks


# 1. Use the register_rich_text_features hook.
@hooks.register("register_rich_text_features")
def register_h4_feature(features):
    """
    Registering the `h4` inline feature.
    """
    feature_name = "inline-h4"
    type_ = "inline-h4"
    tag = "span"

    # 2. Configure how Draftail handles the feature in its toolbar.
    control = {
        "type": type_,
        "label": "inH4",
        "description": "Inline H4",
        # This isn’t even required – Draftail has predefined styles for MARK.
    }

    # 3. Call register_editor_plugin to register the configuration for Draftail.
    features.register_editor_plugin(
        "draftail", feature_name, draftail_features.InlineStyleFeature(control)
    )

    # 4.configure the content transform from the DB to the editor and back.
    db_conversion = {
        "from_database_format": {f"{tag}[class=h4]": InlineStyleElementHandler(type_)},
        "to_database_format": {
            "style_map": {type_: {"element": tag, "props": {"class": "h4"}}}
        },
    }

    # 5. Call register_converter_rule to register the content transformation conversion.
    features.register_converter_rule("contentstate", feature_name, db_conversion)

    # 6. (optional) Add the feature to the default features list to make it available
    # on rich text fields that do not specify an explicit 'features' list
    features.default_features.append("inline-h4")


@hooks.register("register_rich_text_features")
def register_h3_feature(features):
    """
    Registering the `h3` inline feature.
    """
    feature_name = "inline-h3"
    type_ = "inline-h3"
    tag = "p"

    # 2. Configure how Draftail handles the feature in its toolbar.
    control = {
        "type": type_,
        "label": "inh3",
        "description": "Inline h3",
        # This isn’t even required – Draftail has predefined styles for MARK.
    }

    # 3. Call register_editor_plugin to register the configuration for Draftail.
    features.register_editor_plugin(
        "draftail", feature_name, draftail_features.InlineStyleFeature(control)
    )

    # 4.configure the content transform from the DB to the editor and back.
    db_conversion = {
        "from_database_format": {f"{tag}[class=h3]": InlineStyleElementHandler(type_)},
        "to_database_format": {
            "style_map": {type_: {"element": tag, "props": {"class": "h3"}}}
        },
    }

    # 5. Call register_converter_rule to register the content transformation conversion.
    features.register_converter_rule("contentstate", feature_name, db_conversion)

    # 6. (optional) Add the feature to the default features list to make it available
    # on rich text fields that do not specify an explicit 'features' list
    features.default_features.append("inline-h3")


@hooks.register("register_rich_text_features")
def register_text_l_feature(features):
    """
    Registering the `text-l` class.
    """
    feature_name = "inline-text-l"
    type_ = "inline-text-l"
    tag = "p"

    # 2. Configure how Draftail handles the feature in its toolbar.
    control = {
        "type": type_,
        "label": "intext-l",
        "description": "Inline text-l",
        # This isn’t even required – Draftail has predefined styles for MARK.
    }

    # 3. Call register_editor_plugin to register the configuration for Draftail.
    features.register_editor_plugin(
        "draftail", feature_name, draftail_features.InlineStyleFeature(control)
    )

    # 4.configure the content transform from the DB to the editor and back.
    db_conversion = {
        "from_database_format": {
            f"{tag}[class=text-l]": InlineStyleElementHandler(type_)
        },
        "to_database_format": {
            "style_map": {type_: {"element": tag, "props": {"class": "text-l"}}}
        },
    }

    # 5. Call register_converter_rule to register the content transformation conversion.
    features.register_converter_rule("contentstate", feature_name, db_conversion)

    # 6. (optional) Add the feature to the default features list to make it available
    # on rich text fields that do not specify an explicit 'features' list
    features.default_features.append("inline-text-l")
