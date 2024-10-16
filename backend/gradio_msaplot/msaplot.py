from __future__ import annotations

import json
from typing import Any, List, Dict, Optional, Literal, ClassVar
from gradio.components import Component
from gradio.data_classes import FileData, GradioModel
from gradio.events import Events, EventListener

import matplotlib.pyplot as plt
import io
import base64

# Import functions from msa.py
from .msa import (
    DrawMSA,
    DrawConsensusHisto,
    DrawSeqLogo,
    DrawAnnotation,
    DrawComplexMSA,
    GetColorMap,
)

class MSAPlotData(GradioModel):
    msa: List[str]
    seq_names: Optional[List[str]] = None
    start: Optional[int] = None
    end: Optional[int] = None
    color_map: Optional[Dict[str, List[float]]] = None
    plot_type: Literal["msa", "consensus", "logo", "annotation", "complex"] = "msa"
    panels: List[str] = ["msa"]
    panel_height_ratios: Optional[List[float]] = None
    panel_params: Optional[List[Dict[str, Any]]] = None
    wrap: Optional[int] = None
    figsize: Optional[List[float]] = None
    annotations: Optional[List[List[Any]]] = None

    EVENTS: ClassVar[List[Events | EventListener]] = [] 

    def __init__(self, data: Any = None, **kwargs):
        super().__init__(**kwargs)
        if data is not None:
            self.__dict__.update(data)
            
    @classmethod
    def get_events(cls) -> Dict[str, Any]:
        return {}  # MSAPlotData has no events

    @classmethod
    def get_description(cls) -> str:
        return "Helper class for MSAPlot data"
    
class MSAPlot(Component):
    """
    Creates a Multiple Sequence Alignment (MSA) plot component.
    """

    # EVENTS = {
    #     "change": None,
    #     "clear": None
    # }
    EVENTS = [
        Events.change,
        EventListener("clear", doc="Triggered when the plot is cleared.")
    ]

    data_model = MSAPlotData
    def __init__(
        self,
        value: Any | None = None,
        *,
        label: str | None = None,
        every: float | None = None,
        show_label: bool | None = None,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | None = None,
    ):
        super().__init__(
            label=label,
            every=every,
            show_label=show_label,
            container=container,
            scale=scale,
            min_width=min_width,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            value=value,
        )

    def preprocess(self, payload: MSAPlotData | None) -> MSAPlotData | None:
        return payload

    def postprocess(self, value: MSAPlotData) -> Dict[str, Any]:
        if value is None:
            return None

        fig, ax = plt.subplots(figsize=value.figsize or (10, 5))

        color_map = value.color_map or GetColorMap(msa=value.msa)

        if value.plot_type == "msa":
            DrawMSA(value.msa, seq_names=value.seq_names, start=value.start, end=value.end, color_map=color_map, ax=ax)
        elif value.plot_type == "consensus":
            DrawConsensusHisto(value.msa, color_map=color_map, start=value.start, end=value.end, ax=ax)
        elif value.plot_type == "logo":
            DrawSeqLogo(value.msa, color_map=color_map, start=value.start, end=value.end, ax=ax)
        elif value.plot_type == "annotation":
            if value.annotations:
                DrawAnnotation(value.msa, value.annotations, color_map=color_map, start=value.start, end=value.end, ax=ax)
            else:
                raise ValueError("Annotations are required for annotation plot type")
        elif value.plot_type == "complex":
            panel_functions = {
                "msa": DrawMSA,
                "consensus": DrawConsensusHisto,
                "logo": DrawSeqLogo,
                "annotation": DrawAnnotation,
            }
            panels = [panel_functions[p] for p in value.panels]
            DrawComplexMSA(
                value.msa,
                panels=panels,
                seq_names=value.seq_names,
                panel_height_ratios=value.panel_height_ratios,
                panel_params=value.panel_params,
                color_map=color_map,
                start=value.start,
                end=value.end,
                wrap=value.wrap,
                figsize=value.figsize,
            )

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close(fig)

        return {
            "type": "matplotlib",
            "plot": f"data:image/png;base64,{img_base64}",
        }

    def example_payload(self) -> Any:
        return MSAPlotData(
            msa=[
                "ATGCATGC",
                "ATG-ATGC",
                "ATGCATGC",
            ],
            seq_names=["Seq1", "Seq2", "Seq3"],
            plot_type="complex",
            panels=["msa", "consensus", "logo"],
        )

    def example_value(self) -> Any:
        return self.example_payload()

    @classmethod
    def get_events(cls) -> Dict[str, Any]:
        return {event.value if isinstance(event, Events) else event.name: event.doc for event in cls.EVENTS}

    @classmethod
    def get_description(cls) -> str:
        return "Creates a Multiple Sequence Alignment (MSA) plot component."
      
    def api_info(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "msa": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of sequences in the multiple sequence alignment",
                },
                "seq_names": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of sequence names",
                },
                "plot_type": {
                    "type": "string",
                    "enum": ["msa", "consensus", "logo", "annotation", "complex"],
                    "description": "Type of plot to generate",
                },
                "panels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of panels to include in a complex plot",
                },
            },
            "required": ["msa"],
        }   