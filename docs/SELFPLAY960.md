# Chess 47 against itself: the rules check

`python3 tools/selfplay47.py 2 2 7 960`: CHESS47 in the C47 simulator plays itself (key 9), python-chess checks every move, the board after it and the end of the game.

| level | seed | result | plies | clock W | clock B | check |
|---|---|---|---|---|---|---|
| 2 | 207 | DRAW: REPETITION | 89 | 5:00 | 5:00 | rules kept |
| 2 | 208 | DRAW: REPETITION | 66 | 5:00 | 5:00 | rules kept |

## The games

**Level 2, seed 207, Chess960 No 518: DRAW: REPETITION**

1. d4 d5 2. Nd2 Nc6 3. Ngf3 e5 4. dxe5 Nge7 5. e4 a5 6. a4 h5 7. c4 Be6 8. cxd5 Nxd5 9. exd5 Qxd5 10. h4 Nxe5 11. Nxe5 Qxe5+ 12. Be2 b5 13. axb5 f5 14. g4 fxg4 15. O-O g5 16. hxg5 Qxg5 17. Ne4 Qe5 18. f3 g3 19. Qd3 Bb4 20. f4 Qg7 21. Qxg3 Qxg3+ 22. Nxg3 a4 23. Nxh5 O-O 24. Be3 Kh8 25. f5 Bxf5 26. Nf4 Be4 27. Bd3 Bxd3 28. Nxd3 Rxf1+ 29. Rxf1 Bd6 30. Rf7 Ra5 31. b6 cxb6 32. Bxb6 Rb5 33. Bd4+ Kg8 34. Ne5 Bxe5 35. Rd7 Bxd4+ 36. Rxd4 Rxb2 37. Rxa4 Kh8 38. Ra7 Rc2 39. Kh1 Rb2 40. Rc7 Ra2 41. Rb7 Rc2 42. Ra7 Rb2 43. Rc7 Ra2 44. Rb7 Rc2 45. Ra7

**Level 2, seed 208, Chess960 No 285: DRAW: REPETITION**

1. d4 d5 2. Nb3 Nb6 3. e3 e6 4. f4 f5 5. g4 g5 6. gxf5 Rxf5 7. h4 gxh4 8. Nd3 h5 9. Nbc5 a5 10. a4 Nc4 11. b4 axb4 12. Rxb4 b5 13. axb5 Ned6 14. Ne5 Nxe5 15. dxe5 Nxb5 16. c4 dxc4 17. Rxc4 Bf7 18. Qe4 h3 19. Bf2 h2 20. Rh1 h4 21. Rxh2 h3 22. Kb1 Qh6 23. Ka1 Be7 24. Be2 Be8 25. Bd3 c6 26. Be1 Rb6 27. Bd2 Kb8 28. Bb4 Ka8 29. Rh1 h2 30. Bd2 Rb8 31. Bb4 Rb6 32. Bd2 Rb8 33. Bb4 Rb6

