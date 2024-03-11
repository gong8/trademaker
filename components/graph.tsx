import { createChart, ColorType, Time, WhitespaceData, CandlestickData, LineData, UTCTimestamp } from 'lightweight-charts';
import React, { CSSProperties, FC, useEffect, useRef } from 'react';

export type GraphData = CandlestickData<UTCTimestamp>[];
export type EmaData = LineData<UTCTimestamp>[];

export interface GraphProps {
  data: GraphData;
	ema?: EmaData;
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
	ema,
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
			
			if (ema) {
				const emaSeries = chart.addLineSeries({ });
				emaSeries.setData(ema);
			}
			
			addEventListener('resize', handleResize);

			return () => {
				removeEventListener('resize', handleResize);
				chart.remove();
			};
		},
		[data, backgroundColor, ema]
	);

	return (
		<div ref={chartContainerRef} style={style} />
	);
};