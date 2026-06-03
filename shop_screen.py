import pygame
import progress

TAB_UPGRADES = 0
TAB_RUN_GEAR = 1
TAB_LABELS = ["[UPGRADES]", "[RUN GEAR]"]


def _upgrade_rows() -> list:
    rows = []
    for key, defn in progress.UPGRADE_DEFS.items():
        rows.append({"type": "upgrade", "key": key, "defn": defn})
    return rows


def _run_gear_rows() -> list:
    rows = []
    for key, defn in progress.RUN_GEAR_DEFS.items():
        rows.append({"type": "run_gear", "key": key, "defn": defn})
    return rows


def get_rows(tab: int) -> list:
    return _upgrade_rows() if tab == TAB_UPGRADES else _run_gear_rows()


def draw_shop(screen, font, small_font, tab, selected_idx):
    sw, sh = screen.get_size()
    screen.fill("black")

    title = font.render("SHOP", True, (255, 215, 0))
    screen.blit(title, ((sw - title.get_width()) // 2, 20))

    tokens_surf = small_font.render(f"Tokens: {progress.get_tokens()}", True, (255, 215, 0))
    screen.blit(tokens_surf, (sw - tokens_surf.get_width() - 20, 20))

    # Tab headers
    tab_y = 65
    for i, label in enumerate(TAB_LABELS):
        active = i == tab
        color = (255, 255, 100) if active else (120, 120, 120)
        surf = small_font.render(label, True, color)
        x = sw // 2 - 110 + i * 140
        screen.blit(surf, (x, tab_y))
        if active:
            pygame.draw.line(screen, (255, 255, 100), (x, tab_y + surf.get_height() + 2), (x + surf.get_width(), tab_y + surf.get_height() + 2), 2)

    hint_tab = small_font.render("[LEFT/RIGHT] Switch tab", True, (70, 70, 70))
    screen.blit(hint_tab, ((sw - hint_tab.get_width()) // 2, tab_y + 22))

    pygame.draw.line(screen, (60, 60, 60), (sw // 8, 100), (7 * sw // 8, 100), 1)

    rows = get_rows(tab)
    start_y = 115
    row_h = 46

    for i, row in enumerate(rows):
        y = start_y + i * row_h
        is_selected = i == selected_idx

        if is_selected:
            pygame.draw.rect(screen, (30, 30, 60), (sw // 8, y - 2, 6 * sw // 8, row_h - 4), border_radius=4)

        cursor = "> " if is_selected else "  "
        name_color = (255, 255, 180) if is_selected else (200, 200, 200)

        if row["type"] == "upgrade":
            key = row["key"]
            defn = row["defn"]
            tier = progress.get_upgrade(key)
            max_tier = defn["max_tier"]
            tier_label = f"Tier {tier}/{max_tier}"
            next_cost = progress.get_upgrade_next_cost(key)
            desc = defn["desc"][tier]

            name_surf = small_font.render(f"{cursor}{defn['name']}", True, name_color)
            screen.blit(name_surf, (sw // 8 + 10, y + 4))

            tier_surf = small_font.render(tier_label, True, (160, 160, 160))
            screen.blit(tier_surf, (sw // 2 - tier_surf.get_width() // 2, y + 4))

            desc_surf = small_font.render(desc, True, (140, 140, 140))
            screen.blit(desc_surf, (sw // 2 - desc_surf.get_width() // 2, y + 24))

            if next_cost is None:
                cost_surf = small_font.render("MAXED", True, (100, 220, 100))
            elif progress.get_tokens() >= next_cost:
                cost_surf = small_font.render(f"Buy: {next_cost} tokens", True, (100, 220, 100))
            else:
                cost_surf = small_font.render(f"Need: {next_cost} tokens", True, (180, 60, 60))
            screen.blit(cost_surf, (7 * sw // 8 - cost_surf.get_width() - 10, y + 4))

            if is_selected:
                refund_val = progress.get_upgrade_refund_value(key)
                if refund_val is not None:
                    refund_surf = small_font.render(f"[BKSP] Refund: +{refund_val}", True, (160, 120, 80))
                    screen.blit(refund_surf, (7 * sw // 8 - refund_surf.get_width() - 10, y + 24))

        else:  # run gear
            key = row["key"]
            defn = row["defn"]
            qty = progress.get_run_gear().get(key, 0)
            max_qty = defn["max_qty"]
            qty_label = f"Owned: {qty}/{max_qty}"

            name_surf = small_font.render(f"{cursor}{defn['name']}", True, name_color)
            screen.blit(name_surf, (sw // 8 + 10, y + 4))

            desc_surf = small_font.render(defn["desc"], True, (140, 140, 140))
            screen.blit(desc_surf, (sw // 2 - desc_surf.get_width() // 2, y + 24))

            qty_surf = small_font.render(qty_label, True, (160, 160, 160))
            screen.blit(qty_surf, (sw // 2 - qty_surf.get_width() // 2, y + 4))

            if qty >= max_qty:
                cost_surf = small_font.render("FULL", True, (100, 180, 100))
            elif progress.get_tokens() >= defn["cost"]:
                cost_surf = small_font.render(f"Buy: {defn['cost']} tokens", True, (100, 220, 100))
            else:
                cost_surf = small_font.render(f"Need: {defn['cost']} tokens", True, (180, 60, 60))
            screen.blit(cost_surf, (7 * sw // 8 - cost_surf.get_width() - 10, y + 4))

    hint_y = sh - 50
    if tab == TAB_UPGRADES:
        hint = small_font.render("[ENTER] Buy    [BKSP] Refund    [ESC] Back", True, (100, 100, 100))
    else:
        hint = small_font.render("[ENTER] Buy    [ESC] Back", True, (100, 100, 100))
    screen.blit(hint, ((sw - hint.get_width()) // 2, hint_y))


def handle_shop_event(event, tab, selected_idx) -> tuple:
    if event.type != pygame.KEYDOWN:
        return None, tab, selected_idx
    if event.key == pygame.K_ESCAPE:
        return "back", tab, selected_idx
    rows = get_rows(tab)
    if event.key == pygame.K_LEFT:
        new_tab = (tab - 1) % 2
        return None, new_tab, min(selected_idx, len(get_rows(new_tab)) - 1)
    if event.key == pygame.K_RIGHT:
        new_tab = (tab + 1) % 2
        return None, new_tab, min(selected_idx, len(get_rows(new_tab)) - 1)
    if not rows:
        return None, tab, selected_idx
    if event.key == pygame.K_UP:
        return None, tab, (selected_idx - 1) % len(rows)
    if event.key == pygame.K_DOWN:
        return None, tab, (selected_idx + 1) % len(rows)
    if event.key == pygame.K_RETURN:
        row = rows[selected_idx]
        if row["type"] == "upgrade":
            success = progress.buy_upgrade(row["key"])
            return ("bought" if success else "cant_afford"), tab, selected_idx
        else:
            success = progress.buy_run_gear(row["key"])
            return ("bought" if success else "cant_afford"), tab, selected_idx
    if event.key == pygame.K_BACKSPACE and tab == TAB_UPGRADES:
        row = rows[selected_idx]
        if row["type"] == "upgrade":
            success = progress.refund_upgrade(row["key"])
            return ("refunded" if success else None), tab, selected_idx
    return None, tab, selected_idx
