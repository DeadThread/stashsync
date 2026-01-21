def bind_stash_events(widgets, studio_image_data, performer_images_data, current_scene_data, stash_session, QUERY):
    from utils.lookup_utils import lookup, on_id_changed
    from utils.upload_utils import generate_and_upload
    from config import HAMSTER_API_KEY, HAMSTER_UPLOAD_URL

    # ID entry key release
    widgets["stash_id_entry"].bind(
        "<KeyRelease>",
        lambda e: on_id_changed(
            e,
            widgets["stash_id_entry"],
            lambda: lookup(
                widgets["stash_id_entry"],
                widgets["studio_var"],
                widgets["title_var"],
                widgets["desc_text"],
                widgets["tags_text"],
                widgets["generate_btn"],
                widgets["studio_image_label"],
                widgets["performer_scrollable"],
                studio_image_data,
                performer_images_data,
                current_scene_data,
                stash_session,
                QUERY,
                STASH_GRAPHQL_URL
            )
        )
    )

    # Generate button
    def on_generate_click():
        bbcode_lines = generate_and_upload(
            current_scene_data=current_scene_data,
            studio_image_data=studio_image_data,
            performer_images_data=performer_images_data,
            title_var=widgets["title_var"],
            hamster_api_key=HAMSTER_API_KEY,
            hamster_upload_url=HAMSTER_UPLOAD_URL,
        )
        if bbcode_lines:
            widgets["bbcode_text"].delete("1.0", tk.END)
            widgets["bbcode_text"].insert("1.0", "\n".join(bbcode_lines))

    widgets["generate_btn"].config(command=on_generate_click)
