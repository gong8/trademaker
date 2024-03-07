import { createChart, ColorType, Time, WhitespaceData, CandlestickData } from 'lightweight-charts';
import React, { CSSProperties, FC, useEffect, useRef } from 'react';

export type GraphData = (CandlestickData<Time> | WhitespaceData<Time>)[];

export interface GraphProps {
  data: GraphData;
  colors?: {
    backgroundColor?: string;
    lineColor?: string;
    textColor?: string;
    areaTopColor?: string;
    areaBottomColor?: string;
  }
	style?: CSSProperties;
}

export const ChartComponent: FC<GraphProps> = ({
  data,
  colors: {
    backgroundColor = 'black',
		textColor = 'white'
  } = {},
	style = {}
}: GraphProps) => {
	const chartContainerRef = useRef<HTMLDivElement>(null);

	useEffect(
		() => {
      const div = chartContainerRef.current;
      if (div === null) {
        return;
      }

			const handleResize = () => {
				chart.applyOptions({ width: div.clientWidth });
			};

			const chart = createChart(div, {
				layout: {
					background: { type: ColorType.Solid, color: backgroundColor },
					textColor,
				},
				width: div.clientWidth,
				height: 300,
			});
			chart.timeScale().fitContent();

			const newSeries = chart.addCandlestickSeries({ });
			newSeries.setData(data);
			addEventListener('resize', handleResize);

			return () => {
				removeEventListener('resize', handleResize);
				chart.remove();
			};
		},
		[data, backgroundColor]
	);

	return (
		<div ref={chartContainerRef} style={style} />
	);
};