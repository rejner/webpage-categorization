import React, { useState, useEffect, useContext } from "react";
import { ControlsContext, TemplatesContext } from "./Templater";
import { colorToSectionMapping } from "./Templater";
import { Element } from "../models/Element";

interface Props {
  el: HTMLElement;
  depth: number;
}

export const RenderElement: React.FC<Props> = ({ el, depth }) => {
  const [isOpen, setOpen] = useState(false);
  const [elementText, setElementText] = useState('');
  const [isSelected, setSelected] = useState(false);
  const [label, setLabel] = useState<string | undefined>(undefined);
  const {selectedLabel, setSelectedLabel, unrollAll, setUnrollAll} = useContext(ControlsContext);
  const {createTemplate, setCreateTemplate, elements, addElement} = useContext(TemplatesContext);

  useEffect(() => {
    if (el.textContent)
        setElementText(el.textContent?.trim());
  }, [el]);

  useEffect(() => {
      setOpen(unrollAll);
  }, [unrollAll]);

  useEffect(() => {
      if (createTemplate && isSelected) {
          let newElement: Element = {
              type: colorToSectionMapping[label!],
              tag: el.tagName.toLowerCase(),
              id: 0,
              id_attr: el.id,
              classes: el.className.split(" ")
          };
          addElement(newElement);
      }
  }, [createTemplate]);



  const toggleOpen = () => {
    setOpen(!isOpen);
  };

  const toggleSelected = () => {
    setSelected(!isSelected);
    setLabel(selectedLabel);
    console.log("weee");
    console.log(selectedLabel);
    };
  
  function extractTopLevelText(el: HTMLElement) {
    let text = "";
    Array.from(el.childNodes).forEach((child) => {
      if (child.nodeType === 3) {
        text += child.textContent;
      }
    });
    return text;
  }

  return (
    <div className={isSelected ? "bg-" + label + " border-left-0 border-primary" : "border-left-0 border-primary"}>

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
              { extractTopLevelText(el).trim().length > 1 &&
                  
                  <div className="bg-dark text-muted"> {Array(depth).fill(0).map((_, index) => <span key={index}>&nbsp;&nbsp;&nbsp;&nbsp;</span>)} &nbsp;&nbsp;&nbsp;&nbsp; {extractTopLevelText(el)} </div>
                   
              }
              {Array.from(el.children).map((child, index) => {

                if (child instanceof HTMLElement) {
                  return <RenderElement key={index.toString() + '-' + (depth+1).toString()} el={child} depth={depth + 1} />;
                }
                return <> </>;
                
              })}
            </>
          )}
          {Array(depth).fill(0).map((_, index) => <span key={index}>&nbsp;&nbsp;&nbsp;&nbsp;</span>)}&nbsp;&nbsp; &lt;/{el.tagName.toLowerCase()}&gt;
              {/* White space character is: &emsp; */}
      
    </div>
  );
};


export default RenderElement;