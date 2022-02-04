def check_fold(player, context):
    """
    Fold or check regardless.
    """
    return 0


def call_any(player, context):
    """
    Call regardless of the bet size.
    Check if there's nothing to call.
    """
    delta = context.max_phase_bet - player._phase_bet
    return min(delta, player.chips)


def prompt_for_input(player, context):
    delta = context.max_phase_bet - player._phase_bet
    print(f"Player: {player.name}")
    print(f"Hand: {player.hand}")
    print(f"Delta: ${delta}, Chips {player.chips}")
    amount = input("Bet amount: ") or 0
    return float(amount)
