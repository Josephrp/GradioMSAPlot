<script lang="ts">
    import type { LoadingStatus } from "@gradio/statustracker";
    import { Block } from "@gradio/atoms";
    import { StatusTracker } from "@gradio/statustracker";
    import type { Gradio } from "@gradio/utils";
    import { Plot as PlotIcon } from "@gradio/icons";

    export let gradio: Gradio<{
        change: never;
        clear: never;
    }>;

    export let value: {
        type: string;
        plot: string;
    } | null = null;
    export let elem_id = "";
    export let elem_classes: string[] = [];
    export let scale: number | null = null;
    export let min_width: number | undefined = undefined;
    export let loading_status: LoadingStatus | undefined = undefined;
    export let mode: "static" | "interactive" = "interactive";
    export let label: string | undefined = undefined;
    export let show_label = true;
    export let container = true;
    export let visible = true;

    $: src = value?.plot || "";
</script>

<Block
    {visible}
    {elem_id}
    {elem_classes}
    {scale}
    {min_width}
    allow_overflow={false}
    padding={true}
    {container}
>
    {#if show_label}
        <label for={elem_id}>{label || "MSA Plot"}</label>
    {/if}

    {#if loading_status}
        <StatusTracker
            autoscroll={gradio.autoscroll}
            i18n={gradio.i18n}
            {...loading_status}
        />
    {/if}

    {#if src}
        <img {src} alt="MSA Plot" style="width: 100%; height: auto;" />
    {:else}
        <div class="placeholder">
            <PlotIcon />
            <p>{gradio.i18n("plot.no_plot")}</p>
        </div>
    {/if}
</Block>

<style>
    .placeholder {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100%;
        color: var(--color-text-subdued);
    }
</style>