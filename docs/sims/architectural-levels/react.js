import React, { useState } from 'react';

const ArchitectureView = () => {
  const [zoomLevel, setZoomLevel] = useState(1);
  
  const DrawBox = ({ x, y, width, height, label, color = '#B0C4DE', fontSize = 16 }) => (
    <g>
      <rect 
        x={x} 
        y={y} 
        width={width} 
        height={height} 
        fill={color}
        stroke="black"
        strokeWidth="2"
        rx="5"
      />
      <text 
        x={x + width/2} 
        y={y + height/2} 
        textAnchor="middle" 
        dominantBaseline="middle"
        fontSize={fontSize}
      >
        {label}
      </text>
    </g>
  );
  
  const DrawArrow = ({ x1, y1, x2, y2, label }) => (
    <g>
      <line 
        x1={x1} 
        y1={y1} 
        x2={x2} 
        y2={y2} 
        stroke="black" 
        strokeWidth="2"
        markerEnd="url(#arrowhead)"
        markerStart="url(#arrowhead)"
      />
      {label && (
        <text 
          x={(x1 + x2)/2} 
          y={(y1 + y2)/2} 
          textAnchor="middle" 
          dominantBaseline="middle"
          fontSize={14}
        >
          {label}
        </text>
      )}
    </g>
  );

  const renderLevel = () => {
    switch(zoomLevel) {
      case 1:
        return (
          <DrawBox 
            x={150} 
            y={100} 
            width={300} 
            height={200} 
            label="Clock" 
            fontSize={24}
          />
        );
      
      case 2:
        return (
          <g>
            <DrawBox x={150} y={50} width={300} height={100} label="Display" />
            <DrawBox x={150} y={250} width={300} height={100} label="Microcontroller" />
          </g>
        );
      
      case 3:
        return (
          <g>
            <DrawBox x={150} y={50} width={300} height={100} label="Display" />
            <DrawArrow x1={300} y1={150} x2={300} y2={250} label="SPI Bus" />
            <DrawBox x={150} y={250} width={300} height={100} label="Microcontroller" />
          </g>
        );
      
      case 4:
        return (
          <g>
            <DrawBox x={150} y={50} width={300} height={100} label="Display" />
            <DrawArrow x1={300} y1={150} x2={300} y2={250} label="SPI Bus" />
            <DrawBox x={150} y={250} width={300} height={100} label="Microcontroller" />
            <DrawBox x={500} y={250} width={100} height={100} label="RTC" />
          </g>
        );
      
      case 5:
        return (
          <g>
            <DrawBox x={150} y={50} width={300} height={100} label="Display" />
            <DrawArrow x1={300} y1={150} x2={300} y2={250} label="SPI Bus" />
            <DrawBox x={150} y={250} width={300} height={100} label="Microcontroller" />
            <DrawBox x={500} y={250} width={100} height={100} label="RTC" />
            <DrawArrow x1={450} y1={300} x2={500} y2={300} label="I2C Bus" />
          </g>
        );
      
      case 6:
        return (
          <g>
            <DrawBox x={150} y={50} width={300} height={100} label="Display" />
            <DrawArrow x1={300} y1={150} x2={300} y2={250} label="SPI Bus" />
            <DrawBox x={150} y={250} width={300} height={100} label="Microcontroller" />
            <DrawBox x={500} y={250} width={100} height={100} label="RTC" />
            <DrawArrow x1={450} y1={300} x2={500} y2={300} label="I2C Bus" />
            <DrawBox x={20} y={250} width={80} height={100} label="Buttons" />
          </g>
        );
      
      case 7:
        return (
          <g>
            <DrawBox x={150} y={50} width={300} height={100} label="Display" />
            <DrawArrow x1={300} y1={150} x2={300} y2={250} label="SPI Bus" />
            <DrawBox x={150} y={250} width={300} height={100} label="Microcontroller" />
            <DrawBox x={500} y={250} width={100} height={100} label="RTC" />
            <DrawArrow x1={450} y1={300} x2={500} y2={300} label="I2C Bus" />
            <DrawBox x={20} y={250} width={80} height={100} label="Buttons" />
            <DrawBox x={150} y={400} width={450} height={50} label="Power" color="#FFD700" />
          </g>
        );
      
      case 8:
        return (
          <g>
            <DrawBox x={150} y={50} width={300} height={100} label="Display" />
            <DrawArrow x1={300} y1={150} x2={300} y2={250} label="SPI Bus" />
            <DrawBox x={150} y={250} width={300} height={100} label="Microcontroller" />
            <DrawBox x={500} y={250} width={100} height={100} label="RTC" />
            <DrawArrow x1={450} y1={300} x2={500} y2={300} label="I2C Bus" />
            <DrawBox x={20} y={250} width={80} height={100} label="Buttons" />
            <DrawBox x={20} y={150} width={80} height={80} label="Speaker" />
            <DrawBox x={150} y={400} width={450} height={50} label="Power" color="#FFD700" />
          </g>
        );
      
      case 9:
        return (
          <g>
            <DrawBox x={150} y={50} width={300} height={100} label="Display" />
            <DrawArrow x1={300} y1={150} x2={300} y2={250} label="SPI Bus" />
            <g>
              <DrawBox x={150} y={250} width={300} height={100} label="" />
              <DrawBox x={170} y={260} width={120} height={35} label="Core 1" color="#E6E6FA" />
              <DrawBox x={170} y={305} width={120} height={35} label="Core 2" color="#E6E6FA" />
              <text x={300} y={300} textAnchor="middle">Microcontroller</text>
            </g>
            <DrawBox x={500} y={250} width={100} height={100} label="RTC" />
            <DrawArrow x1={450} y1={300} x2={500} y2={300} label="I2C Bus" />
            <DrawBox x={20} y={250} width={80} height={100} label="Buttons" />
            <DrawBox x={20} y={150} width={80} height={80} label="Speaker" />
            <DrawBox x={150} y={400} width={450} height={50} label="Power" color="#FFD700" />
          </g>
        );
      
      case 10:
        return (
          <g>
            <DrawBox x={150} y={50} width={300} height={100} label="Display" />
            <DrawArrow x1={300} y1={150} x2={300} y2={250} label="SPI Bus" />
            <g>
              <DrawBox x={150} y={250} width={300} height={100} label="" />
              <DrawBox x={170} y={260} width={120} height={35} label="Core 1" color="#E6E6FA" />
              <DrawBox x={170} y={305} width={120} height={35} label="Core 2" color="#E6E6FA" />
              <DrawBox x={300} y={260} width={120} height={80} label="PIO" color="#E6E6FA" />
              <text x={300} y={300} textAnchor="middle">Microcontroller</text>
            </g>
            <DrawBox x={500} y={250} width={100} height={100} label="RTC" />
            <DrawArrow x1={450} y1={300} x2={500} y2={300} label="I2C Bus" />
            <DrawBox x={20} y={250} width={80} height={100} label="Buttons" />
            <DrawBox x={20} y={150} width={80} height={80} label="Speaker" />
            <DrawBox x={150} y={400} width={450} height={50} label="Power" color="#FFD700" />
          </g>
        );
      
      default:
        return null;
    }
  };

  return (
    <div className="flex flex-col items-center w-full max-w-4xl mx-auto p-4">
      <svg width="650" height="500" className="border border-gray-300">
        <defs>
          <marker
            id="arrowhead"
            markerWidth="10"
            markerHeight="7"
            refX="9"
            refY="3.5"
            orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="black" />
          </marker>
        </defs>
        {renderLevel()}
      </svg>
      <div className="w-full mt-4 flex items-center gap-4">
        <span className="text-sm">Zoom Level: {zoomLevel}</span>
        <input
          type="range"
          min="1"
          max="10"
          value={zoomLevel}
          onChange={(e) => setZoomLevel(parseInt(e.target.value))}
          className="w-full"
        />
      </div>
    </div>
  );
};

export default ArchitectureView;