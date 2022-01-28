def default_policy(player, context):
    """
    Fold or check regardless.
    """
    return 0


def always_call_or_check(player, context):
    delta = context.max_phase_bet - player._phase_bet
    return min(delta, player.chips)


def prompt_for_input(player, context):
    delta = context.max_phase_bet - player._phase_bet
    print(f"Player: {player.name}")
    print(f"Hand: {player.hand}")
    print(f"Delta: ${delta}, Chips {player.chips}")
    amount = input("Bet amount: ") or 0
    return float(amount)
