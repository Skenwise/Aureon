# ADR-2026-02-13-01: Treasury Module Finalization

**Title:** Treasury Module: Cash Positions, Funding Transfers, Liquidity, and Fund Reservations
**Date:** 2026-02-13
**Status:** Accepted
**Context:**
We needed a unified treasury system for the Aureon backend that can:

* Track real-time provider cash positions
* Reserve funds for pending transactions
* Aggregate liquidity across providers
* Handle funding transfers between provider accounts

**Decisions:**

1. **CashPositionProvider**

   * Handles persistence of `CashPosition` records.
   * Provides: `fetch_balance`, `get_cash_position`, `list_cash_positions`, `update_balance`, `create_cash_position`.
   * Does **not** execute reservations, liquidity aggregation, or funding transfers.
   * Added missing methods for reservations in the provider:

     * `reserve_funds` (creates FundReservation and updates CashPosition balances)
     * `release_reservation`
     * `confirm_reservation`

2. **FundingProvider / FundingAdapter**

   * Handles `FundingTransfer` operations: `create_transfer`, `get_transfer`, `list_transfers`, `complete_transfer`, `fail_transfer`, `cancel_transfer`.
   * Uses `FundingTransferCreate` and `FundingTransferRead` schemas.

3. **LiquidityProvider / LiquidityAdapter**

   * Aggregates cash positions to compute total liquidity per currency (`get_liquidity`, `get_total_liquidity`).
   * Supports `check_sufficient_funds`.
   * Returns `LiquidityRead` schema with positions breakdown.

4. **Schemas (Pydantic)**

   * `CashPositionRead`: snapshot of provider account balances
   * `LiquidityRead`: aggregated liquidity with positions
   * `FundingTransferCreate` / `FundingTransferRead`: fund movement between providers
   * `ReserveFundsCreate` / `ReserveFundsRead`: fund reservation before execution
   * `ProviderBalanceRead`: raw external provider balance
   * Removed `ReserveFundsCreate` necessity by allowing a plain dict or `TypedDict` alternative for runtime validation

5. **Adapters**

   * Convert provider models into Pydantic schemas
   * Maintain port interfaces for Cash Positions, Funding Transfers, and Liquidity
   * CashPositionAdapter now fully implements `reserve_funds`, `release_reservation`, and `confirm_reservation`

6. **Error Handling**

   * Used `ValidationError` and `NotFoundError` for all providers
   * Ensures consistent exception flow across treasury operations

**Consequences:**

* Treasury module is now fully functional and modular.
* Providers are isolated; adapters handle schema conversions and port contracts.
* Reservations are atomic and correctly update cash positions.
* Liquidity aggregation works across all currencies and providers.
* Can integrate external APIs for syncing balances without touching core persistence logic.

**Next Steps:**

* Integrate external provider APIs for live balance sync
* Add automated tests for:

  * Reservation creation, release, confirmation
  * Funding transfers success/failure paths
  * Liquidity checks and sufficiency
* Monitor real-time balances and update the cash positions through the `update_balance` method
