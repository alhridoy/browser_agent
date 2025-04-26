import os
import time
import pyautogui
import cv2
import numpy as np
import pytesseract
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional, Union
import json
import csv
import io
import logging
from src.utils.logger import setup_logger

# Setup logger
logger = setup_logger("extractor")

class DataExtractor:
    """
    Extract structured data from web pages.
    """
    
    def __init__(self):
        """
        Initialize the data extractor.
        """
        # Set up Tesseract OCR path if needed
        if os.name == 'nt':  # Windows
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        logger.info("Initialized data extractor")
    
    async def extract(self, extraction_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract data from a web page.
        
        Args:
            extraction_type: The type of extraction to perform (ocr, html, table, list, etc.).
            params: Parameters for the extraction.
            
        Returns:
            A dictionary containing the extracted data.
        """
        try:
            if extraction_type == "ocr":
                return await self._extract_ocr(params.get("region"), params.get("lang", "eng"))
            elif extraction_type == "html":
                return await self._extract_html(params.get("selector"), params.get("attribute"))
            elif extraction_type == "table":
                return await self._extract_table(params.get("selector"), params.get("format", "json"))
            elif extraction_type == "list":
                return await self._extract_list(params.get("selector"), params.get("format", "json"))
            elif extraction_type == "text":
                return await self._extract_text(params.get("selector"))
            elif extraction_type == "image":
                return await self._extract_image(params.get("selector"), params.get("save_path"))
            else:
                return {
                    "success": False,
                    "message": f"Unknown extraction type: {extraction_type}"
                }
        except Exception as e:
            logger.error(f"Error extracting data: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to extract data: {str(e)}"
            }
    
    async def _extract_ocr(self, region: Optional[List[int]] = None, lang: str = "eng") -> Dict[str, Any]:
        """
        Extract text from the screen using OCR.
        
        Args:
            region: The region to extract text from [left, top, width, height].
            lang: The language to use for OCR.
            
        Returns:
            A dictionary containing the extracted text.
        """
        try:
            # Take a screenshot
            if region:
                screenshot = pyautogui.screenshot(region=(region[0], region[1], region[2], region[3]))
            else:
                screenshot = pyautogui.screenshot()
            
            # Convert the screenshot to a numpy array
            screenshot_np = np.array(screenshot)
            
            # Convert to grayscale
            screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)
            
            # Apply thresholding to improve OCR accuracy
            _, screenshot_thresh = cv2.threshold(screenshot_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Extract text using Tesseract OCR
            text = pytesseract.image_to_string(screenshot_thresh, lang=lang)
            
            return {
                "success": True,
                "message": "Extracted text using OCR",
                "data": text
            }
        except Exception as e:
            logger.error(f"Error extracting text using OCR: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to extract text using OCR: {str(e)}"
            }
    
    async def _extract_html(self, selector: str, attribute: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract data from HTML using a CSS selector.
        
        Args:
            selector: The CSS selector to use.
            attribute: The attribute to extract (if None, extract the inner HTML).
            
        Returns:
            A dictionary containing the extracted data.
        """
        try:
            # Get the current URL from the browser
            # For now, we'll use a placeholder URL
            url = "https://example.com"
            
            # Fetch the HTML content
            response = requests.get(url)
            response.raise_for_status()
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, "lxml")
            
            # Find elements matching the selector
            elements = soup.select(selector)
            
            # Extract the data
            data = []
            for element in elements:
                if attribute:
                    if element.has_attr(attribute):
                        data.append(element[attribute])
                else:
                    data.append(element.get_text().strip())
            
            return {
                "success": True,
                "message": f"Extracted data using selector: {selector}",
                "data": data
            }
        except Exception as e:
            logger.error(f"Error extracting HTML data: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to extract HTML data: {str(e)}"
            }
    
    async def _extract_table(self, selector: str, format: str = "json") -> Dict[str, Any]:
        """
        Extract a table from the web page.
        
        Args:
            selector: The CSS selector for the table.
            format: The output format (json or csv).
            
        Returns:
            A dictionary containing the extracted table data.
        """
        try:
            # Get the current URL from the browser
            # For now, we'll use a placeholder URL
            url = "https://example.com"
            
            # Fetch the HTML content
            response = requests.get(url)
            response.raise_for_status()
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, "lxml")
            
            # Find the table
            table = soup.select_one(selector)
            
            if not table:
                return {
                    "success": False,
                    "message": f"Could not find table with selector: {selector}"
                }
            
            # Extract the table headers
            headers = []
            header_row = table.find("thead").find("tr") if table.find("thead") else table.find("tr")
            
            if header_row:
                for th in header_row.find_all(["th", "td"]):
                    headers.append(th.get_text().strip())
            
            # Extract the table rows
            rows = []
            for tr in table.find_all("tr")[1:] if headers else table.find_all("tr"):
                row = []
                for td in tr.find_all("td"):
                    row.append(td.get_text().strip())
                
                if row:
                    rows.append(row)
            
            # Format the data
            if format.lower() == "json":
                if headers:
                    data = []
                    for row in rows:
                        row_data = {}
                        for i, cell in enumerate(row):
                            if i < len(headers):
                                row_data[headers[i]] = cell
                        data.append(row_data)
                else:
                    data = rows
                
                return {
                    "success": True,
                    "message": "Extracted table data",
                    "data": data,
                    "format": "json"
                }
            elif format.lower() == "csv":
                output = io.StringIO()
                writer = csv.writer(output)
                
                if headers:
                    writer.writerow(headers)
                
                writer.writerows(rows)
                
                return {
                    "success": True,
                    "message": "Extracted table data",
                    "data": output.getvalue(),
                    "format": "csv"
                }
            else:
                return {
                    "success": False,
                    "message": f"Unknown format: {format}"
                }
        except Exception as e:
            logger.error(f"Error extracting table data: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to extract table data: {str(e)}"
            }
    
    async def _extract_list(self, selector: str, format: str = "json") -> Dict[str, Any]:
        """
        Extract a list from the web page.
        
        Args:
            selector: The CSS selector for the list.
            format: The output format (json or csv).
            
        Returns:
            A dictionary containing the extracted list data.
        """
        try:
            # Get the current URL from the browser
            # For now, we'll use a placeholder URL
            url = "https://example.com"
            
            # Fetch the HTML content
            response = requests.get(url)
            response.raise_for_status()
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, "lxml")
            
            # Find the list
            list_element = soup.select_one(selector)
            
            if not list_element:
                return {
                    "success": False,
                    "message": f"Could not find list with selector: {selector}"
                }
            
            # Extract the list items
            items = []
            for li in list_element.find_all("li"):
                items.append(li.get_text().strip())
            
            # Format the data
            if format.lower() == "json":
                return {
                    "success": True,
                    "message": "Extracted list data",
                    "data": items,
                    "format": "json"
                }
            elif format.lower() == "csv":
                output = io.StringIO()
                writer = csv.writer(output)
                
                for item in items:
                    writer.writerow([item])
                
                return {
                    "success": True,
                    "message": "Extracted list data",
                    "data": output.getvalue(),
                    "format": "csv"
                }
            else:
                return {
                    "success": False,
                    "message": f"Unknown format: {format}"
                }
        except Exception as e:
            logger.error(f"Error extracting list data: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to extract list data: {str(e)}"
            }
    
    async def _extract_text(self, selector: str) -> Dict[str, Any]:
        """
        Extract text from the web page.
        
        Args:
            selector: The CSS selector for the text element.
            
        Returns:
            A dictionary containing the extracted text.
        """
        try:
            # Get the current URL from the browser
            # For now, we'll use a placeholder URL
            url = "https://example.com"
            
            # Fetch the HTML content
            response = requests.get(url)
            response.raise_for_status()
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, "lxml")
            
            # Find the element
            element = soup.select_one(selector)
            
            if not element:
                return {
                    "success": False,
                    "message": f"Could not find element with selector: {selector}"
                }
            
            # Extract the text
            text = element.get_text().strip()
            
            return {
                "success": True,
                "message": "Extracted text",
                "data": text
            }
        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to extract text: {str(e)}"
            }
    
    async def _extract_image(self, selector: str, save_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract an image from the web page.
        
        Args:
            selector: The CSS selector for the image.
            save_path: The path to save the image to.
            
        Returns:
            A dictionary containing the extracted image data.
        """
        try:
            # Get the current URL from the browser
            # For now, we'll use a placeholder URL
            url = "https://example.com"
            
            # Fetch the HTML content
            response = requests.get(url)
            response.raise_for_status()
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, "lxml")
            
            # Find the image
            img = soup.select_one(selector)
            
            if not img:
                return {
                    "success": False,
                    "message": f"Could not find image with selector: {selector}"
                }
            
            # Get the image URL
            img_url = img.get("src")
            
            if not img_url:
                return {
                    "success": False,
                    "message": "Image does not have a src attribute"
                }
            
            # Make the URL absolute if it's relative
            if not img_url.startswith(("http://", "https://")):
                img_url = f"{url.rstrip('/')}/{img_url.lstrip('/')}"
            
            # Fetch the image
            img_response = requests.get(img_url)
            img_response.raise_for_status()
            
            # Save the image if a save path is provided
            if save_path:
                with open(save_path, "wb") as f:
                    f.write(img_response.content)
            
            return {
                "success": True,
                "message": "Extracted image",
                "data": {
                    "url": img_url,
                    "content_type": img_response.headers.get("Content-Type"),
                    "size": len(img_response.content),
                    "save_path": save_path
                }
            }
        except Exception as e:
            logger.error(f"Error extracting image: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to extract image: {str(e)}"
            }
    
    def save_data(self, data: Any, file_path: str, format: str = "json") -> Dict[str, Any]:
        """
        Save extracted data to a file.
        
        Args:
            data: The data to save.
            file_path: The path to save the data to.
            format: The format to save the data in (json, csv, txt).
            
        Returns:
            A dictionary indicating success or failure.
        """
        try:
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            if format.lower() == "json":
                with open(file_path, "w") as f:
                    json.dump(data, f, indent=2)
            elif format.lower() == "csv":
                if isinstance(data, list) and all(isinstance(item, dict) for item in data):
                    # List of dictionaries
                    with open(file_path, "w", newline="") as f:
                        writer = csv.DictWriter(f, fieldnames=data[0].keys())
                        writer.writeheader()
                        writer.writerows(data)
                elif isinstance(data, list) and all(isinstance(item, list) for item in data):
                    # List of lists
                    with open(file_path, "w", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerows(data)
                else:
                    # Single list
                    with open(file_path, "w", newline="") as f:
                        writer = csv.writer(f)
                        for item in data:
                            writer.writerow([item])
            elif format.lower() == "txt":
                with open(file_path, "w") as f:
                    if isinstance(data, list):
                        f.write("\n".join(str(item) for item in data))
                    else:
                        f.write(str(data))
            else:
                return {
                    "success": False,
                    "message": f"Unknown format: {format}"
                }
            
            return {
                "success": True,
                "message": f"Saved data to {file_path}",
                "file_path": file_path,
                "format": format
            }
        except Exception as e:
            logger.error(f"Error saving data: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to save data: {str(e)}"
            }
