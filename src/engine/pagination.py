"""
Pagination system for handling long text screens in The Sunken Cathedral game.
Allows splitting content across multiple pages with navigation.
"""

import pygame
from typing import List, Tuple, Optional, Callable
from dataclasses import dataclass


@dataclass
class PagedContent:
    """Represents content that can be split across multiple pages."""
    lines: List[str]
    colors: List[Tuple[int, int, int]]  # Color for each line
    title: str = ""


def create_text_content(text_lines: List[str], title: str = "", 
                       title_color: Tuple[int, int, int] = (255, 255, 85),
                       text_color: Tuple[int, int, int] = (255, 255, 255)) -> PagedContent:
    """
    Create PagedContent from a simple list of text lines.
    
    Args:
        text_lines: List of text lines to display
        title: Optional title for the content
        title_color: Color for the title (default: yellow)
        text_color: Color for regular text (default: white)
        
    Returns:
        PagedContent ready for pagination
    """
    lines = []
    colors = []
    
    if title:
        lines.extend([title, ""])
        colors.extend([title_color, text_color])
    
    lines.extend(text_lines)
    colors.extend([text_color] * len(text_lines))
    
    return PagedContent(lines=lines, colors=colors, title="")


class Paginator:
    """
    Handles pagination for long text content.
    Automatically splits content across pages and provides navigation.
    """
    
    def __init__(self, display, lines_per_page: int = None):
        """
        Initialize the paginator.
        
        Args:
            display: The PygameDisplay instance
            lines_per_page: Maximum lines to show per page (auto-calculated if None)
        """
        self.display = display
        self.current_page = 0
        
        # Auto-calculate lines per page to leave room for navigation controls
        if lines_per_page is None:
            # Reserve space for title (50px), navigation controls (80px), and some padding
            usable_height = display.screen_height - 150  # Top padding + bottom controls
            line_height = 25
            self.lines_per_page = max(10, usable_height // line_height)  # Minimum 10 lines
        else:
            self.lines_per_page = lines_per_page
        
    def show_paged_content(self, content: PagedContent, 
                          on_selection: Optional[Callable[[int], None]] = None,
                          selectable_lines: List[int] = None,
                          auto_continue: bool = False) -> Optional[int]:
        """
        Show paginated content with optional selection.
        
        Args:
            content: The content to display
            on_selection: Callback when a line is selected (optional)
            selectable_lines: List of line indices that can be selected
            auto_continue: If True, shows "Press [Enter] to continue..." on last page
            
        Returns:
            Selected line index if selection is enabled, None otherwise
        """
        if selectable_lines is None:
            selectable_lines = []
            
        selected_index = 0
        if selectable_lines:
            selected_index = selectable_lines[0]
        
        total_pages = (len(content.lines) + self.lines_per_page - 1) // self.lines_per_page
        
        while True:
            # Calculate page bounds
            start_line = self.current_page * self.lines_per_page
            end_line = min(start_line + self.lines_per_page, len(content.lines))
            
            # Clear screen
            self.display.screen.fill((0, 0, 0))
            
            # Draw title if provided
            y_offset = 50
            if content.title:
                self.display.draw_text_at_pixel(content.title, 50, y_offset, (255, 255, 85))
                y_offset += 50
            
            # Draw page content
            line_height = 25
            page_lines = content.lines[start_line:end_line]
            page_colors = content.colors[start_line:end_line]
            
            # Add "Press [Enter] to continue..." on the last page if auto_continue is enabled
            is_last_page = (self.current_page == total_pages - 1)
            if auto_continue and is_last_page and not selectable_lines:
                # Add some spacing and the continue message
                page_lines = page_lines + ["", "Press [Enter] to continue..."]
                page_colors = page_colors + [(255, 255, 255), (128, 128, 128)]
            
            for i, (line, color) in enumerate(zip(page_lines, page_colors)):
                if i < len(content.lines[start_line:end_line]):  # Original content
                    actual_line_index = start_line + i
                    
                    # Highlight selected line if selectable
                    if selectable_lines and actual_line_index == selected_index:
                        # Draw selection background
                        selection_rect = pygame.Rect(45, y_offset + i * line_height - 2, 
                                                    self.display.screen_width - 90, line_height)
                        pygame.draw.rect(self.display.screen, (32, 32, 64), selection_rect)
                        color = (255, 255, 255)  # White text on selection
                
                self.display.draw_text_at_pixel(line, 50, y_offset + i * line_height, color)
            
            # Draw compact navigation help (retro style)
            nav_y = self.display.screen_height - 60
            
            # Line 1: Page indicator
            if total_pages > 1:
                page_line = f"Page {self.current_page + 1} of {total_pages}"
            else:
                page_line = ""
            
            # Line 2: Compact controls (using ASCII characters like old games)
            if total_pages > 1 and selectable_lines:
                controls_line = "[<][>] next/prev [^][v] select [Enter] confirm [Esc] back/cancel"
            elif total_pages > 1:
                controls_line = "[<][>] next/prev [Enter] continue [Esc] back/cancel"
            elif selectable_lines:
                controls_line = "[^][v] select [Enter] confirm [Esc] back/cancel"
            else:
                controls_line = "[Enter] continue [Esc] back/cancel"
            
            # Draw the two lines
            if page_line:
                self.display.draw_text_at_pixel(page_line, 50, nav_y, (128, 128, 128))
                self.display.draw_text_at_pixel(controls_line, 50, nav_y + 20, (128, 128, 128))
            else:
                self.display.draw_text_at_pixel(controls_line, 50, nav_y + 10, (128, 128, 128))
            
            pygame.display.flip()
            
            # Handle input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "QUIT_REQUESTED"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT and self.current_page > 0:
                        self.current_page -= 1
                    elif event.key == pygame.K_RIGHT and self.current_page < total_pages - 1:
                        self.current_page += 1
                    elif event.key == pygame.K_UP and selectable_lines:
                        # Find previous selectable line
                        current_idx = selectable_lines.index(selected_index) if selected_index in selectable_lines else 0
                        selected_index = selectable_lines[(current_idx - 1) % len(selectable_lines)]
                        # Change page if needed
                        self._ensure_line_visible(selected_index, total_pages)
                    elif event.key == pygame.K_DOWN and selectable_lines:
                        # Find next selectable line
                        current_idx = selectable_lines.index(selected_index) if selected_index in selectable_lines else 0
                        selected_index = selectable_lines[(current_idx + 1) % len(selectable_lines)]
                        # Change page if needed
                        self._ensure_line_visible(selected_index, total_pages)
                    elif event.key == pygame.K_RETURN:
                        if selectable_lines and on_selection:
                            on_selection(selected_index)
                            return selected_index
                        elif not selectable_lines:
                            return None  # Just continue
                    elif event.key == pygame.K_ESCAPE:
                        if selectable_lines:
                            return None  # Just cancel selection
                        else:
                            return "QUIT_REQUESTED"  # Quit requested from non-selectable screen
    
    def _ensure_line_visible(self, line_index: int, total_pages: int) -> None:
        """Ensure the specified line is visible on the current page."""
        required_page = line_index // self.lines_per_page
        if required_page != self.current_page and required_page < total_pages:
            self.current_page = required_page 