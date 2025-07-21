init python:
    # Ambient track templates for different locations
    ambient_templates = {
        "street_ambient": [
            {"track_id": "street_base", "filename": "audio/street_base.ogg", "track_type": "mandatory", "volume": 0.5, "fade_in_time": 4.0, "fade_out_time": 4.0},
            {"track_id": "car_horn", "filename": "audio/car_horn.ogg", "track_type": "random", "volume": 0.3, "play_chance": 0.2, "min_duration": 10, "max_duration": 30, "fade_in_time": 2.0, "fade_out_time": 2.0},
        ],
        "forest_ambient": [
            {"track_id": "forest_base", "filename": "audio/forest_base.ogg", "track_type": "mandatory", "volume": 0.6, "fade_in_time": 5.0, "fade_out_time": 3.0},
            {"track_id": "birds", "filename": "audio/birds.ogg", "track_type": "random", "volume": 0.4, "play_chance": 0.3, "min_duration": 20, "max_duration": 60, "fade_in_time": 3.0, "fade_out_time": 2.0},
        ],
    }

    def apply_ambient_template(ambient, template_name):
        """
        Adds all tracks from the specified template to the ambient system.
        ambient: instance of DynamicAmbientSystem
        template_name: key from ambient_templates
        """
        if template_name not in ambient_templates:
            raise ValueError("Unknown ambient template: %s" % template_name)
        for params in ambient_templates[template_name]:
            ambient.add_track(**params) 