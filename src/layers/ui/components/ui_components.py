"""
UI Components - Reusable UI building blocks.
Components encapsulate common interactions (buttons, inputs, dropdowns, etc.)
"""

from typing import Any, Optional, List

from src.core.base_page import BasePageObject
from src.core.enums import LocatorStrategy, WaitStrategy
from src.core.exceptions import ElementNotFoundError, ElementNotVisibleError
from src.layers.ui.locators.base_locator import Locator


class BaseComponent:
    """
    Base class for all UI components.
    Components are reusable UI units smaller than pages but larger than locators.
    
    - Encapsulate element interactions
    - Support multiple locator strategies
    - Provide consistent interface across apps
    """

    def __init__(self, page: BasePageObject, locator: Locator, component_name: str = "BaseComponent"):
        """
        Initialize component.
        
        Args:
            page: Parent BasePageObject instance
            locator: Locator for this component
            component_name: Name for logging
        """
        self.page = page
        self.locator = locator
        self.component_name = component_name
        self._logger = page.logger

    def find(self, timeout_ms: int = 15000) -> Any:
        """Find the component element."""
        return self.page.find_element(
            self.locator.value,
            self.locator.strategy,
            timeout_ms
        )

    def is_visible(self, timeout_ms: int = 2000) -> bool:
        """Check if component is visible."""
        return self.page.is_visible(
            self.locator.value,
            self.locator.strategy,
            timeout_ms
        )

    def wait_for_visible(self, timeout_ms: int = 15000) -> None:
        """Wait for component to be visible."""
        element = self.find(timeout_ms)
        self.page.wait_for_element(element, WaitStrategy.VISIBLE, timeout_ms)


class TextInputComponent(BaseComponent):
    """
    Text input component (input fields, text areas).
    
    Usage:
        username_input = TextInputComponent(
            page,
            Locator(LocatorStrategy.ID, "username"),
            "Username Input"
        )
        username_input.fill("john_doe")
        value = username_input.get_value()
    """

    def fill(self, text: str, clear_first: bool = True) -> None:
        """Fill text input with value."""
        if clear_first:
            element = self.find()
            element.clear()
        self.page.fill_text(self.locator.value, text, self.locator.strategy)
        self._logger.debug(f"Filled {self.component_name} with text")

    def get_value(self) -> str:
        """Get text input value."""
        element = self.find()
        value = element.input_value()
        self._logger.debug(f"Got value from {self.component_name}: {value}")
        return value

    def clear(self) -> None:
        """Clear text input."""
        element = self.find()
        element.clear()
        self._logger.debug(f"Cleared {self.component_name}")

    def get_placeholder(self) -> str:
        """Get input placeholder text."""
        element = self.find()
        placeholder = element.get_attribute("placeholder") or ""
        return placeholder


class ButtonComponent(BaseComponent):
    """
    Button component.
    
    Usage:
        submit_btn = ButtonComponent(
            page,
            Locator(LocatorStrategy.CSS, "button.submit"),
            "Submit Button"
        )
        submit_btn.click()
        submit_btn.wait_for_enabled()
    """

    def click(self, timeout_ms: int = 15000) -> None:
        """Click button."""
        self.page.click(self.locator.value, self.locator.strategy, timeout_ms)
        self._logger.debug(f"Clicked {self.component_name}")

    def double_click(self, timeout_ms: int = 15000) -> None:
        """Double click button."""
        element = self.find(timeout_ms)
        element.dblclick()
        self._logger.debug(f"Double clicked {self.component_name}")

    def is_enabled(self) -> bool:
        """Check if button is enabled."""
        return self.page.is_enabled(self.locator.value, self.locator.strategy)

    def wait_for_enabled(self, timeout_ms: int = 15000) -> None:
        """Wait for button to be enabled."""
        element = self.find(timeout_ms)
        self.page.wait_for_element(element, WaitStrategy.ENABLED, timeout_ms)

    def get_text(self) -> str:
        """Get button text."""
        return self.page.get_text(self.locator.value, self.locator.strategy)


class DropdownComponent(BaseComponent):
    """
    Dropdown/Select component.
    
    Usage:
        country_dropdown = DropdownComponent(
            page,
            Locator(LocatorStrategy.ID, "country"),
            "Country Dropdown"
        )
        country_dropdown.select("USA")
        selected = country_dropdown.get_selected_value()
    """

    def select(self, value: str, timeout_ms: int = 15000) -> None:
        """Select option from dropdown."""
        self.page.select_option(self.locator.value, value, self.locator.strategy, timeout_ms)
        self._logger.debug(f"Selected '{value}' from {self.component_name}")

    def get_selected_value(self) -> str:
        """Get currently selected value."""
        element = self.find()
        # Get the value of the selected option
        selected = element.evaluate("el => el.value")
        return selected or ""

    def get_selected_text(self) -> str:
        """Get text of selected option."""
        element = self.find()
        selected_text = element.evaluate("el => el.options[el.selectedIndex].text")
        return selected_text or ""

    def get_all_options(self) -> List[str]:
        """Get all available options."""
        element = self.find()
        options = element.evaluate(
            "el => Array.from(el.options, option => option.value)"
        )
        return options or []


class CheckboxComponent(BaseComponent):
    """
    Checkbox component.
    
    Usage:
        agree_checkbox = CheckboxComponent(
            page,
            Locator(LocatorStrategy.ID, "terms"),
            "Terms Checkbox"
        )
        agree_checkbox.check()
        is_checked = agree_checkbox.is_checked()
    """

    def check(self, timeout_ms: int = 15000) -> None:
        """Check the checkbox."""
        element = self.find(timeout_ms)
        if not element.is_checked():
            element.check()
            self._logger.debug(f"Checked {self.component_name}")

    def uncheck(self, timeout_ms: int = 15000) -> None:
        """Uncheck the checkbox."""
        element = self.find(timeout_ms)
        if element.is_checked():
            element.uncheck()
            self._logger.debug(f"Unchecked {self.component_name}")

    def is_checked(self) -> bool:
        """Check if checkbox is checked."""
        element = self.find()
        return element.is_checked()

    def toggle(self) -> None:
        """Toggle checkbox state."""
        element = self.find()
        element.click()
        self._logger.debug(f"Toggled {self.component_name}")


class TableComponent(BaseComponent):
    """
    Table component for reading data from tables.
    
    Usage:
        users_table = TableComponent(
            page,
            Locator(LocatorStrategy.CSS, "table.users"),
            "Users Table"
        )
        rows = users_table.get_all_rows()
        cell = users_table.get_cell_value(1, 2)
    """

    def get_all_rows(self) -> List[dict]:
        """Get all rows from table as dictionaries."""
        element = self.find()
        rows = element.evaluate(
            """(el) => {
                const headers = Array.from(el.querySelectorAll('thead th, tr:first th'))
                    .map(h => h.textContent.trim());
                const data = [];
                const tbody = el.querySelector('tbody') || el;
                Array.from(tbody.querySelectorAll('tr')).forEach(row => {
                    const cells = Array.from(row.querySelectorAll('td'));
                    const rowData = {};
                    headers.forEach((h, i) => {
                        rowData[h] = cells[i]?.textContent.trim() || '';
                    });
                    data.push(rowData);
                });
                return data;
            }"""
        )
        self._logger.debug(f"Retrieved {len(rows)} rows from {self.component_name}")
        return rows

    def get_cell_value(self, row: int, col: int) -> str:
        """Get cell value by row and column index."""
        element = self.find()
        value = element.evaluate(
            f"""(el) => {{
                const cell = el.querySelector(`tr:nth-child({row}) td:nth-child({col})`);
                return cell ? cell.textContent.trim() : '';
            }}"""
        )
        return value or ""

    def get_row_count(self) -> int:
        """Get total number of rows."""
        element = self.find()
        count = element.evaluate(
            "(el) => (el.querySelector('tbody') || el).querySelectorAll('tr').length"
        )
        return count or 0

    def search_row_by_value(self, search_value: str, column_index: int = 0) -> Optional[dict]:
        """Find row containing specific value."""
        element = self.find()
        row_data = element.evaluate(
            f"""(el, val, col) => {{
                const rows = (el.querySelector('tbody') || el).querySelectorAll('tr');
                for (let row of rows) {{
                    const cell = row.querySelectorAll('td')[col];
                    if (cell && cell.textContent.includes(val)) {{
                        return Array.from(row.querySelectorAll('td')).map(c => c.textContent.trim());
                    }}
                }}
                return null;
            }}""",
            search_value,
            column_index
        )
        return row_data
