

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class NavPage:
    key: str
    label: str
    icon: str = ""
    module: str = ""


@dataclass(frozen=True)
class NavGroup:
    key: str
    label: str
    icon: str = ""
    pages: tuple[NavPage, ...] = field(default_factory=tuple)


NAV_HOME = NavPage(
    key="dashboard",
    label="Dashboard",
    
    module="pages_content.dashboard_preview",
)

NAV_GROUPS: tuple[NavGroup, ...] = (
    NavGroup(
        key="pipeline",
        label="Pipeline",
        
        pages=(
            NavPage(
                key="ai_workspace",
                label="AI Workspace",
                module="pages/1_AI_Workspace.py",
            ),
            NavPage(
                key="reports",
                label="Analytics & Reports",
                module="pages/2_Analytics_Reports.py",
            ),
        ),
    ),
)


def group_for_page(page_key: str) -> str | None:
    for group in NAV_GROUPS:
        if any(p.key == page_key for p in group.pages):
            return group.key
    return None


def find_page_label(page_key: str) -> str | None:
    if page_key == NAV_HOME.key:
        return NAV_HOME.label
    for group in NAV_GROUPS:
        for page in group.pages:
            if page.key == page_key:
                return page.label
    return None


def find_page_module(page_key: str) -> str | None:
    if page_key == NAV_HOME.key:
        return NAV_HOME.module
    for group in NAV_GROUPS:
        for page in group.pages:
            if page.key == page_key:
                return page.module
    return None
