# How to change default images

Step by step guide to replacing default images in project. Applies
to all image files in the project currently.

1. Select default image
2. Go to either existing project directory or setup new project.
3. Open data folder.
4. Open fonts folder.
5. Move .tff files into fonts folder
6. Open fonts.yaml in text editor
7. Add font in following way at bottom of fonts list

    font_name: font_file_name

8. Save yaml file.
9. Font will now be selectable in Fonts dropdown in gui