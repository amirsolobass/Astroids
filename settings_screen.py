import pygame
import progress

STUB_LABEL = "(Coming Soon)"


def build_settings_items() -> list:
    items = []
    for feature in progress.TOGGLEABLE_FEATURES:
        if feature in progress._unlocked:
            items.append({"key": feature, "stub": False})
    for feature in sorted(progress.STUB_FEATURES):
        if feature in progress._unlocked:
            items.append({"key": feature, "stub": True})
    return items


def draw_settings(screen, font, small_font, items, selected_idx):
    sw, sh = screen.get_size()
    screen.fill("black")

    title = font.render("SETTINGS", True, "white")
    screen.blit(title, ((sw - title.get_width()) // 2, 30))

    subtitle = small_font.render("Feature Toggles", True, (160, 160, 160))
    screen.blit(subtitle, ((sw - subtitle.get_width()) // 2, 80))

    pygame.draw.line(screen, (60, 60, 60), (sw // 4, 105), (3 * sw // 4, 105), 1)

    start_y = 125
    row_h = 38

    if not items:
        msg = small_font.render("No features unlocked yet.", True, (120, 120, 120))
        screen.blit(msg, ((sw - msg.get_width()) // 2, start_y + 30))
    else:
        for i, item in enumerate(items):
            y = start_y + i * row_h
            is_selected = i == selected_idx
            key = item["key"]
            name = progress.UNLOCK_NAMES.get(key, key)

            if is_selected:
                pygame.draw.rect(screen, (30, 30, 60), (sw // 8, y - 4, 6 * sw // 8, row_h - 4), border_radius=4)

            cursor = "> " if is_selected else "  "
            label_color = (255, 255, 180) if is_selected else (200, 200, 200)
            label = small_font.render(f"{cursor}{name}", True, label_color)
            screen.blit(label, (sw // 8 + 10, y + 4))

            if item["stub"]:
                stub_surf = small_font.render(STUB_LABEL, True, (100, 100, 100))
                screen.blit(stub_surf, (6 * sw // 8 - stub_surf.get_width() - 20, y + 4))
            else:
                enabled = progress.is_enabled(key)
                state_text = "[ON ]" if enabled else "[OFF]"
                state_color = (80, 220, 80) if enabled else (180, 60, 60)
                state_surf = small_font.render(state_text, True, state_color)
                screen.blit(state_surf, (6 * sw // 8 - state_surf.get_width() - 20, y + 4))

    hint_y = sh - 50
    hint = small_font.render("[SPACE/ENTER] Toggle    [ESC] Back", True, (100, 100, 100))
    screen.blit(hint, ((sw - hint.get_width()) // 2, hint_y))


def handle_settings_event(event, items, selected_idx) -> tuple:
    if event.type != pygame.KEYDOWN:
        return None, selected_idx
    if event.key == pygame.K_ESCAPE:
        return "back", selected_idx
    if not items:
        return None, selected_idx
    if event.key == pygame.K_UP:
        return None, (selected_idx - 1) % len(items)
    if event.key == pygame.K_DOWN:
        return None, (selected_idx + 1) % len(items)
    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
        item = items[selected_idx]
        if not item["stub"]:
            progress.toggle_feature(item["key"])
        return None, selected_idx
    return None, selected_idx
