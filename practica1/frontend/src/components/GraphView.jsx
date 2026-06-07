import ForceGraph2D from "react-force-graph-2d";

export default function GraphView({
    graphData
}) {

    if (
        !graphData ||
        !graphData.nodes?.length
    ) {

        return (
            <div className="graph-container">
                No hay datos para mostrar
            </div>
        );
    }

    return (
        <div className="graph-container">

            <ForceGraph2D

                graphData={graphData}

                width={1100}
                height={650}

                cooldownTicks={100}

                backgroundColor="#ffffff"

                enableNodeDrag={false}

                nodeLabel="id"

                linkWidth={2}

                nodeCanvasObject={(
                    node,
                    ctx
                ) => {

                    ctx.beginPath();

                    ctx.arc(
                        node.x,
                        node.y,
                        18,
                        0,
                        2 * Math.PI
                    );

                    ctx.fillStyle =
                        "#ea580c";

                    ctx.fill();

                    ctx.font =
                        "12px Arial";

                    ctx.fillStyle =
                        "#111827";

                    ctx.textAlign =
                        "center";

                    ctx.fillText(
                        node.id,
                        node.x,
                        node.y + 35
                    );
                }}

            />

        </div>
    );
}