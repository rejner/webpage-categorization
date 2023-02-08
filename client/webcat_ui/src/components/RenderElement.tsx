import React, { useState, useEffect, useContext } from "react";
import { ControlsContext } from "./Templater";

interface Props {
  el: HTMLElement;
  depth: number;
}

const RenderElement: React.FC<Props> = ({ el, depth }) => {
  const [isOpen, setOpen] = useState(false);
  const [elementText, setElementText] = useState('');
  const [isSelected, setSelected] = useState(false);
  const [label, setLabel] = useState<string | undefined>(undefined);
  const {selectedLabel, setSelectedLabel} = useContext(ControlsContext);

  useEffect(() => {
    if (el.textContent)
        setElementText(el.textContent?.trim());
  }, [el]);

  const toggleOpen = () => {
    setOpen(!isOpen);
  };

  const toggleSelected = () => {
    setSelected(!isSelected);
    setLabel(selectedLabel);
    console.log("weee");
    console.log(selectedLabel);
    };

  return (
    <div key={el.innerHTML}  className={isSelected ? "bg-" + label + " border-left-0 border-primary" : "border-left-0 border-primary"}>

        <>
          <div style={{ cursor: 'pointer' }} className="border-top border-dark">
            {/* Put &nbsp; times depth */}
            {Array(depth).fill(0).map((_, index) => <span key={index}>&nbsp;&nbsp;&nbsp;&nbsp;</span>)}
            <span onClick={toggleOpen}>{isOpen ? '\u25BE' : '\u25B8'}</span>
            <span onClick={toggleSelected}>
                &lt;{el.tagName.toLowerCase()}
                {el.id && ` id="${el.id}"`}
                {el.className && ` class="${el.className}"`}&gt;
            </span>
          </div>
          {isOpen && (
            <>
              {//elementText && <div>{elementText}</div>}
                }
              {Array.from(el.children).map((child, index) => {
                // if tagname is not p, span or strong, then render it

                if (child instanceof HTMLElement && !['p', 'span', 'strong', 'a'].includes(child.tagName.toLowerCase())) {
                  return <RenderElement key={index} el={child} depth={depth + 1} />;
                }
                return <> <div className="bg-dark text-muted"> {Array(depth).fill(0).map((_, index) => <span key={index}>&nbsp;&nbsp;&nbsp;&nbsp;</span>)} &nbsp;&nbsp;&nbsp;&nbsp; {child.innerHTML} </div> </>;
              })}
            </>
          )}
          {Array(depth).fill(0).map((_, index) => <span key={index}>&nbsp;&nbsp;&nbsp;&nbsp;</span>)}&nbsp;&nbsp; &lt;/{el.tagName.toLowerCase()}&gt;
              {/* White space character is: &emsp; */}
        </>
      
    </div>
  );

  /* 
  return (
    <div key={el.innerHTML} style={{ paddingLeft: depth * 4 }} className="border-left-0 border-primary">
      {el.tagName === 'DIV' ? (
        <>
          <div onClick={toggleOpen} style={{ cursor: 'pointer' }}>
            {isOpen ? '▼' : '►'} &lt;{el.tagName.toLowerCase()}
            {el.id && ` id="${el.id}"`}
            {el.className && ` class="${el.className}"`}&gt;
          </div>
          {isOpen && (
            <>
              {//elementText && <div>{elementText}</div>}
                }
              {Array.from(el.children).map((child, index) => {
                if (child instanceof HTMLElement) {
                  return <RenderElement key={index} el={child} depth={depth + 1} />;
                }
                return child.textContent;
              })}
            </>
          )}
          &lt;/{el.tagName.toLowerCase()}&gt;
        </>
      ) : (
        <>
          &lt;{el.tagName.toLowerCase()}
          {el.id && ` id="${el.id}"`}
          {el.className && ` class="${el.className}"`}&gt;
          {//elementText && <div>{elementText}</div>}
            }
          {Array.from(el.children).map((child, index) => {
            if (child instanceof HTMLElement) {
              return <RenderElement key={index} el={child} depth={depth + 1} />;
            }
            return child.textContent;
          })}
          &lt;/{el.tagName.toLowerCase()}&gt;
        </>
      )}
    </div>
  );
  */
};


export default RenderElement;