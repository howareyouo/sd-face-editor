import os

import gradio as gr
from modules import script_callbacks, shared

from scripts.entities.option import Option
from scripts.io.util import inferencers_dir
from scripts.ui import workflow_editor
from scripts.ui.param_value_parser import ParamValueParser


class UiBuilder:
    def __init__(self, for_extension: bool) -> None:
        self.infotext_fields: list = []
        self.__for_extension = for_extension

    def build(self, is_img2img: bool):
        if self.__for_extension:
            with gr.Accordion("Face Editor", open=False, elem_id="sd-face-editor-extension"):
                return self.__build()
        else:
            self.__create_workflow_selector()
            return self.__build()

    def __create_workflow_selector(self) -> gr.Dropdown:
        return gr.Dropdown(choices=workflow_editor.get_files(), label="Workflow", value="default", elem_classes="flex-0")

    def __build(self):
        enabled = gr.Checkbox(label="Enabled", value=False)
        self.infotext_fields.append((enabled, Option.add_prefix("enabled")))

        with gr.Row():
            use_minimal_area = gr.Checkbox(label="Use minimal area", value=Option.DEFAULT_USE_MINIMAL_AREA)
            self.infotext_fields.append((use_minimal_area, Option.add_prefix("use_minimal_area")))
        
            save_original_image = gr.Checkbox(label="Save original image", value=Option.DEFAULT_SAVE_ORIGINAL_IMAGE)
            self.infotext_fields.append((save_original_image, Option.add_prefix("save_original_image")))

            show_original_image = gr.Checkbox(label="Show original image", value=Option.DEFAULT_SHOW_ORIGINAL_IMAGE)
            self.infotext_fields.append((show_original_image, Option.add_prefix("show_original_image")))

            show_intermediate_steps = gr.Checkbox(label="Show intermediate steps", value=Option.DEFAULT_SHOW_INTERMEDIATE_STEPS)
            self.infotext_fields.append((show_intermediate_steps, Option.add_prefix("show_intermediate_steps")))

        with gr.Row():
            prompt_for_face = gr.Textbox(show_label=False,placeholder="Prompt for face",label="Prompt for face",lines=2)
            self.infotext_fields.append((prompt_for_face, Option.add_prefix("prompt_for_face")))
            workflow_selector = self.__create_workflow_selector()

        affected_areas = gr.CheckboxGroup(
            label="Affected areas", choices=["Face", "Hair", "Hat", "Neck"], value=Option.DEFAULT_AFFECTED_AREAS
        )

        affected_areas_key = Option.add_prefix("affected_areas")
        self.infotext_fields.append((affected_areas, affected_areas_key))
        ParamValueParser.add(affected_areas_key, list)

        with gr.Row():
            mask_size = gr.Slider(label="Mask size", minimum=0, maximum=64, step=1, value=Option.DEFAULT_MASK_SIZE)
            self.infotext_fields.append((mask_size, Option.add_prefix("mask_size")))

            mask_blur = gr.Slider(label="Mask blur ", minimum=0, maximum=64, step=1, value=Option.DEFAULT_MASK_BLUR)
            self.infotext_fields.append((mask_blur, Option.add_prefix("mask_blur")))

        with gr.Accordion("Advanced Options", open=False):
            gr.HTML("(1) Face Detection:")
            with gr.Row():
                max_face_count = gr.Slider(minimum=1, maximum=20, step=1, value=Option.DEFAULT_MAX_FACE_COUNT,
                    label="Maximum number of faces to detect",
                )
                self.infotext_fields.append((max_face_count, Option.add_prefix("max_face_count")))

                confidence = gr.Slider(minimum=0.7, maximum=1.0, step=0.01, value=Option.DEFAULT_CONFIDENCE,
                    label="Face detection confidence",
                )
                self.infotext_fields.append((confidence, Option.add_prefix("confidence")))

            gr.HTML("(2) Crop and Resize the Faces:")
            with gr.Row():
                face_margin = gr.Slider(
                    minimum=1.0, maximum=2.0, step=0.1, value=Option.DEFAULT_FACE_MARGIN, label="Face margin"
                )
                self.infotext_fields.append((face_margin, Option.add_prefix("face_margin")))

                upscalers = [upscaler.name for upscaler in shared.sd_upscalers]
                if Option.DEFAULT_UPSCALER not in upscalers: 
                    upscalers.append(Option.DEFAULT_UPSCALER)
                upscaler = gr.Dropdown(
                    label="Upscaler",
                    show_label=False,
                    choices=[upscaler.name for upscaler in shared.sd_upscalers],
                    value=Option.DEFAULT_UPSCALER,
                )
                self.infotext_fields.append((upscaler, Option.add_prefix("upscaler")))

            with gr.Row():
                face_size = gr.Slider(label="Size of the face when recreating",
                    minimum=64, maximum=2048, step=16, value=Option.DEFAULT_FACE_SIZE,
                )
                self.infotext_fields.append((face_size, Option.add_prefix("face_size")))
                ignore_larger_faces = gr.Checkbox(label="Ignore faces larger than specified size", 
                    value=Option.DEFAULT_IGNORE_LARGER_FACES
                )
                self.infotext_fields.append((ignore_larger_faces, Option.add_prefix("ignore_larger_faces")))

            gr.HTML("(3) Recreate the Faces")
            with gr.Row():
                strength1 = gr.Slider(
                    label="Denoising strength for face images",
                    value=Option.DEFAULT_STRENGTH1,
                    minimum=0.1,
                    maximum=0.8,
                    step=0.05,
                )
                self.infotext_fields.append((strength1, Option.add_prefix("strength1")))

                tilt_adjustment_threshold = gr.Slider(
                    label="Tilt adjustment threshold",
                    value=Option.DEFAULT_TILT_ADJUSTMENT_THRESHOLD,
                    minimum=0,
                    maximum=180,
                    step=10,
                )
                self.infotext_fields.append((tilt_adjustment_threshold, Option.add_prefix("tilt_adjustment_threshold")))

            apply_scripts_to_faces = gr.Checkbox(
                label="Apply scripts to faces", visible=False, value=Option.DEFAULT_APPLY_SCRIPTS_TO_FACES
            )
            self.infotext_fields.append((apply_scripts_to_faces, Option.add_prefix("apply_scripts_to_faces")))

            with gr.Row():
                strength2 = gr.Slider(
                    label="Denoising strength for the entire image ",
                    value=Option.DEFAULT_STRENGTH2,
                    minimum=0.0,
                    maximum=1.0,
                    step=0.05,
                )
                self.infotext_fields.append((strength2, Option.add_prefix("strength2")))

                apply_inside_mask_only = gr.Checkbox(
                    label="Apply inside mask only ", value=Option.DEFAULT_APPLY_INSIDE_MASK_ONLY
                )
                self.infotext_fields.append((apply_inside_mask_only, Option.add_prefix("apply_inside_mask_only")))

        with gr.Accordion("Workflow Editor", open=False):
            workflow = workflow_editor.build(workflow_selector)
            self.infotext_fields.append((workflow, Option.add_prefix("workflow")))

        return [
            workflow_selector,
            face_margin,
            confidence,
            strength1,
            strength2,
            max_face_count,
            mask_size,
            mask_blur,
            prompt_for_face,
            apply_inside_mask_only,
            save_original_image,
            show_intermediate_steps,
            apply_scripts_to_faces,
            face_size,
            use_minimal_area,
            ignore_larger_faces,
            affected_areas,
            show_original_image,
            workflow,
            upscaler,
            tilt_adjustment_threshold,
        ]


def on_ui_settings():
    section = ("face_editor", "Face Editor")

    shared.opts.add_option(
        "face_editor_search_subdirectories",
        shared.OptionInfo(False, "Search workflows in subdirectories", gr.Checkbox, section=section),
    )

    additional_components = []
    with os.scandir(inferencers_dir) as entries:
        for entry in entries:
            if entry.is_dir() and entry.name[0].isalnum():
                additional_components.append(entry.name)

    shared.opts.add_option(
        "face_editor_additional_components",
        shared.OptionInfo(
            [], "Additional components", gr.CheckboxGroup, {"choices": additional_components}, section=section
        ),
    )

    shared.opts.add_option(
        "face_editor_save_original_on_detection_fail",
        shared.OptionInfo(True, "Save original image if face detection fails", gr.Checkbox, section=section),
    )

    shared.opts.add_option(
        "face_editor_correct_tilt",
        shared.OptionInfo(False, "Adjust tilt for detected faces", gr.Checkbox, section=section),
    )

    shared.opts.add_option(
        "face_editor_script_index",
        shared.OptionInfo(
            99,
            "The position in postprocess at which this script will be executed; "
            "0 means it will be executed before any scripts, 99 means it will probably be executed last.",
            gr.Slider,
            {"minimum": 0, "maximum": 99, "step": 1},
            section=section,
        ),
    )


script_callbacks.on_ui_settings(on_ui_settings)
