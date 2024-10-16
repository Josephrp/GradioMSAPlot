
import gradio as gr
from gradio_msaplot import MSAPlot, MSAPlotData
import matplotlib
matplotlib.use('Agg')

example = MSAPlot().example_value()

with gr.Blocks() as demo:
    with gr.Row():
        MSAPlot(label="Blank"),  # blank component
        MSAPlot(value=example, label="Populated"),  # populated component


if __name__ == "__main__":
    demo.launch()
