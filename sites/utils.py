import uuid

# section attribute types
# we know how much of an update we need to do depending on this.
TEXT = "TEXT"
VIDEO = "VIDEO"
IMAGE = "IMAGE"
IMAGE_WITH_TEXT = 'IMAGE_WITH_TEXT'
VIDEO_WITH_TEXT = "VIDEO_WITH_TEXT"
NEWSLETTER = "NEWSLETTER"
PRODUCTS = "PRODUCTS"
CATEGORIES = "CATEGORIES"
COLUMNS = "COLUMNS"
LINK_ICON = "LINK_ICON"
LAYOUT = "LAYOUT"
STYLE = "STYLE"
AVATAR_IMAGE = "AVATAR_IMAGE"
BACKGROUND_IMAGE = "BACKGROUND_IMAGE"
TESTIMONIAL_PHOTO = "TESTIMONIAL_PHOTO"
URL = "URL"
IMAGE_POSITION = "IMAGE_POSITION"
VIDEO_POSITION = "VIDEO_POSITION"
BOOLEAN = "BOOLEAN"
INTEGER = "INTEGER"


def build_page_section(section_type):
    """

    :param section_type:
    :return:
    """
    if section_type == "TEXT":
        return {
            "section_type": "TEXT",
            "data_section_uuid": str(uuid.uuid4()),
            "title": {
                "data_attribute_uuid": str(uuid.uuid4()),
                "value": 'Text Title',
                "attribute_type": TEXT
            },
            "body": {
                "data_attribute_uuid": str(uuid.uuid4()),
                "value": "Text Body",
                "attribute_type": TEXT
            }
        }
    elif section_type == "BIO":
        return {
            "section_type": "BIO",
            "data_section_uuid": str(uuid.uuid4()),
            "layout": {
                "data_attribute_uuid": str(uuid.uuid4()),
                "attribute_type": LAYOUT,
                "value": "VERTICAL"
            },
            "style": {
                "data_attribute_uuid": str(uuid.uuid4()),
                "attribute_type": STYLE,
                "value": "NORMAL"
            },
            "title": {
                "data_attribute_uuid": str(uuid.uuid4()),
                "value": 'Bio',
                "attribute_type": TEXT
            },
            "text": {
                "data_attribute_uuid": str(uuid.uuid4()),
                "attribute_type": TEXT,
                "value": "All about me..."
            },
            "avatar": {
                "data_attribute_uuid": str(uuid.uuid4()),
                "attribute_type": AVATAR_IMAGE,
                "value": None
            },
            "background_image": {
                "data_attribute_uuid": str(uuid.uuid4()),
                "attribute_type": BACKGROUND_IMAGE,
                "value": None
            },
            "twitter": {
                "data_attribute_uuid": str(uuid.uuid4()),
                "attribute_type": LINK_ICON,
                "value": None
            },
            "instagram": {
                "data_attribute_uuid": str(uuid.uuid4()),
                "attribute_type": LINK_ICON,
                "value": None
            },
            "facebook": {
                "data_attribute_uuid": str(uuid.uuid4()),
                "attribute_type": LINK_ICON,
                "value": None
            },
            "website": {
                "data_attribute_uuid": str(uuid.uuid4()),
                "attribute_type": LINK_ICON,
                "value": None
            }
        }
    elif section_type == "TESTIMONIALS":
        return {
            "section_type": "TESTIMONIALS",
            "data_section_uuid": str(uuid.uuid4()),
            "style": {
                "data_attribute_uuid": str(uuid.uuid4()),
                "attribute_type": STYLE,
                "value": "NORMAL"
            },
            "title": {
                "data_attribute_uuid": str(uuid.uuid4()),
                "value": 'Testimonials',
                "attribute_type": TEXT
            },
            "testimonials": [
                {
                    "data_testimonial_uuid": str(uuid.uuid4()),
                    "name": {
                        "data_attribute_uuid": str(uuid.uuid4()),
                        "attribute_type": TEXT,
                        "value": "Jane Doe"
                    },
                    "text": {
                        "data_attribute_uuid": str(uuid.uuid4()),
                        "attribute_type": TEXT,
                        "value": "Write something here."
                    },
                    "photo": {
                        "data_attribute_uuid": str(uuid.uuid4()),
                        "attribute_type": TESTIMONIAL_PHOTO,
                        "value": None
                    },
                }
            ]
        }
    elif section_type == "FAQ":
        return {
            "section_type": "FAQ",
            "data_section_uuid": str(uuid.uuid4()),
            "style": {
                "data_attribute_uuid": str(uuid.uuid4()),
                "attribute_type": STYLE,
                "value": "NORMAL"
            },
            "title": {
                "data_attribute_uuid": str(uuid.uuid4()),
                "value": 'FAQ',
                "attribute_type": TEXT
            },
            "questions": [
                {
                    "data_faq_uuid": str(uuid.uuid4()),
                    "question": {
                        "data_attribute_uuid": str(uuid.uuid4()),
                        "attribute_type": TEXT,
                        "value": "How do I sign up?"
                    },
                    "answer": {
                        "data_attribute_uuid": str(uuid.uuid4()),
                        "attribute_type": TEXT,
                        "value": "Just click the buy button."
                    }
                }
            ]
        }
    elif section_type == IMAGE_WITH_TEXT:
        return {
            "section_type": IMAGE_WITH_TEXT,
            "data_section_uuid": str(uuid.uuid4()),
            "style": {
                "data_attribute_uuid": str(uuid.uuid4()),
                "attribute_type": STYLE,
                "value": "NORMAL"
            },
            "title": {
                "data_attribute_uuid": str(uuid.uuid4()),
                "value": 'Title',
                "attribute_type": TEXT
            },
            "text": {
                "data_attribute_uuid": str(uuid.uuid4()),
                "attribute_type": TEXT,
                "value": "Lorem ipsum dolor sit amet..."
            },
            "image": {
                "data_attribute_uuid": str(uuid.uuid4()),
                "attribute_type": IMAGE,
                "value": None
            },
            "image_position": {
                "data_attribute_uuid": str(uuid.uuid4()),
                "attribute_type": IMAGE_POSITION,
                "value": "LEFT"
            },
            "button_text": {
                "data_attribute_uuid": str(uuid.uuid4()),
                "value": 'Click me',
                "attribute_type": TEXT
            },
            "button_url": {
                "data_attribute_uuid": str(uuid.uuid4()),
                "value": '',
                "attribute_type": URL
            }
        }
    elif section_type == VIDEO_WITH_TEXT:
        return {
            "section_type": VIDEO_WITH_TEXT,
            "data_section_uuid": str(uuid.uuid4()),
            "style": {
                "data_attribute_uuid": str(uuid.uuid4()),
                "attribute_type": STYLE,
                "value": "NORMAL"
            },
            "title": {
                "data_attribute_uuid": str(uuid.uuid4()),
                "value": 'Title',
                "attribute_type": TEXT
            },
            "text": {
                "data_attribute_uuid": str(uuid.uuid4()),
                "attribute_type": TEXT,
                "value": "Lorem ipsum dolor sit amet..."
            },
            "video": {
                "data_attribute_uuid": str(uuid.uuid4()),
                "attribute_type": VIDEO,
                "value": None
            },
            "video_position": {
                "data_attribute_uuid": str(uuid.uuid4()),
                "attribute_type": VIDEO_POSITION,
                "value": "LEFT"
            },
            "button_text": {
                "data_attribute_uuid": str(uuid.uuid4()),
                "value": 'Click me',
                "attribute_type": TEXT
            },
            "button_url": {
                "data_attribute_uuid": str(uuid.uuid4()),
                "value": '',
                "attribute_type": URL
            }
        }
    elif section_type == NEWSLETTER:
        return {
            "section_type": NEWSLETTER,
            "data_section_uuid": str(uuid.uuid4()),
            "style": {
                "data_attribute_uuid": str(uuid.uuid4()),
                "attribute_type": STYLE,
                "value": "NORMAL"
            },
            "title": {
                "data_attribute_uuid": str(uuid.uuid4()),
                "value": 'Sign up to our newsletter!',
                "attribute_type": TEXT
            },
            "text": {
                "data_attribute_uuid": str(uuid.uuid4()),
                "attribute_type": TEXT,
                "value": "We'll send you all kinds of exciting stuff."
            },
            "button_text": {
                "data_attribute_uuid": str(uuid.uuid4()),
                "value": 'Subscribe',
                "attribute_type": TEXT
            },
            "capture_first_name": {
                "data_attribute_uuid": str(uuid.uuid4()),
                "attribute_type": BOOLEAN,
                "value": False
            },
            "use_recaptcha": {
                "data_attribute_uuid": str(uuid.uuid4()),
                "attribute_type": BOOLEAN,
                "value": False
            },
            "footer_text": {
                "data_attribute_uuid": str(uuid.uuid4()),
                "attribute_type": TEXT,
                "value": "100% spam free."
            },
            "thank_you_text": {
                "data_attribute_uuid": str(uuid.uuid4()),
                "value": 'Thank you for subscribing.',
                "attribute_type": TEXT
            }
        }
    elif section_type == PRODUCTS:
        return {
            "section_type": PRODUCTS,
            "data_section_uuid": str(uuid.uuid4()),
            "global_section": True
        }
    elif section_type == CATEGORIES:
        return {
            "section_type": CATEGORIES,
            "data_section_uuid": str(uuid.uuid4()),
            "global_section": True
        }
    elif section_type == COLUMNS:
        return {
            "section_type": COLUMNS,
            "data_section_uuid": str(uuid.uuid4()),
            "style": {
                "data_attribute_uuid": str(uuid.uuid4()),
                "attribute_type": STYLE,
                "value": "NORMAL"
            },
            "num_columns": {
                "data_attribute_uuid": str(uuid.uuid4()),
                "attribute_type": INTEGER,
                "value": 2
            },
            "columns": [{
                "data_column_uuid": str(uuid.uuid4()),
                "content": []
            }, {
                "data_column_uuid": str(uuid.uuid4()),
                "content": []
            }]
        }
