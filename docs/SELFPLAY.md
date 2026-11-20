# Chess 47 against itself: the rules check

`python3 tools/selfplay47.py `: CHESS47 in the C47 simulator plays itself (key 9), python-chess checks every move, the board after it and the end of the game.

| level | seed | result | plies | clock W | clock B | check |
|---|---|---|---|---|---|---|
| 0 | 1 | CHECKMATE | 91 | 0:47 | 0:41 | rules kept |
| 0 | 2 | STALEMATE | 168 | 1:10 | 1:30 | rules kept |
| 0 | 3 | unfinished at 290 plies | 290 | 1:53 | 1:43 | rules kept |
| 0 | 4 | DRAW: MATERIAL | 262 | 1:57 | 1:50 | rules kept |
| 0 | 5 | CHECKMATE | 275 | 2:11 | 1:32 | rules kept |
| 1 | 101 | STALEMATE | 93 | 3:24 | 1:55 | rules kept |
| 1 | 102 | DRAW: REPETITION | 74 | 1:26 | 2:15 | rules kept |
| 1 | 103 | STALEMATE | 92 | 1:48 | 2:19 | rules kept |
| 1 | 104 | STALEMATE | 92 | 1:48 | 2:19 | rules kept |
| 1 | 105 | DRAW: MATERIAL | 73 | 1:15 | 2:21 | rules kept |
| 2 | 201 | DRAW: REPETITION | 68 | 5:46 | 7:50 | rules kept |
| 2 | 202 | CHECKMATE | 96 | 7:11 | 8:15 | rules kept |
| 2 | 203 | CHECKMATE | 67 | 5:57 | 4:59 | rules kept |
| 2 | 204 | DRAW: REPETITION | 80 | 8:09 | 7:15 | rules kept |
| 2 | 205 | CHECKMATE | 43 | 6:41 | 4:43 | rules kept |

## The games

**Level 0, seed 1: CHECKMATE**

1. Nf3 Nh6 2. b3 a5 3. g4 Ra7 4. a3 Ra6 5. e3 c6 6. Rg1 b5 7. Bd3 b4 8. Ng5 Nf5 9. c3 Ng3 10. Bc2 Qc7 11. cxb4 Kd8 12. Nh3 f6 13. Rf1 e5 14. d4 Bxb4+ 15. axb4 Qd6 16. fxg3 Qxb4+ 17. Nd2 Ra7 18. Rf5 Qb5 19. Ng1 g6 20. Ra4 c5 21. Bb1 d5 22. dxc5 e4 23. Qc2 Kd7 24. Nh3 Kc6 25. Rxe4 Kc7 26. Qd1 Rd8 27. Ra4 Re8 28. Ba2 Rg8 29. Rxd5 Kc6 30. Bb1 Qb7 31. Ng1 Re8 32. Ndf3 Qb4+ 33. Kf1 Qxb3 34. Ba2 Nd7 35. Rb4 Re4 36. Ke2 Rxb4 37. Qd3 Nb6 38. Qb5+ Kb7 39. Rd3 Ka8 40. Qxa5 Qg8 41. Rd2 Rb1 42. Rd8 Qf7 43. Nh3 h6 44. Ba3 f5 45. Qxb6 Rg1 46. Rxc8#

**Level 0, seed 2: STALEMATE**

1. h4 c6 2. Rh2 h6 3. g3 d6 4. Nh3 g6 5. e4 f5 6. a4 a6 7. Ra3 Rh7 8. b3 Rh8 9. Qf3 Qb6 10. Ng5 f4 11. Nf7 Bg7 12. Qh1 c5 13. Ra1 Bf8 14. Nxh6 e5 15. Qf3 Bxh6 16. gxf4 Nc6 17. Rh1 Bg5 18. Be2 Bf5 19. Bd3 Be6 20. Rh3 Nb4 21. Qg2 Nxd3+ 22. Kf1 c4 23. Re3 Bh6 24. Qh3 Nxf2 25. d4 Nd3 26. h5 Bc8 27. Qh4 exf4 28. Qh1 Nxc1 29. Qh4 Nd3 30. Kg2 Qb4 31. Qh2 c3 32. Kg1 f3 33. Nxc3 Qxa4 34. b4 Ra7 35. Ree1 Qb5 36. Rxa6 Ne5 37. Ra4 Nf7 38. Kh1 Bf5 39. Ra3 Qc4 40. Re2 d5 41. Kg1 g5 42. Ra4 f2+ 43. Kxf2 dxe4 44. Qg3 Qxb4 45. Re3 Qxd4 46. Nd5 Kf8 47. Qb8+ Nd8 48. Ra3 Qe5 49. Ra2 Bg4 50. Qxb7 Qe6 51. Ra5 Rh7 52. Qf7+ Qxf7+ 53. Nf4 Be6 54. c3 Bg4 55. Re5 Rh8 56. Rg3 Qxf4+ 57. Kg2 Kf7 58. Ra5 Qb8 59. Ra2 Nb7 60. Kf1 e3 61. Re2 Bxh5 62. Rg4 Qf8 63. c4 Bg6 64. Rd4 Kf6 65. Rh2 Bh5 66. Rc2 Ra3 67. Rh2 Nd6 68. Ra2 Rc3 69. Ra1 Rxc4 70. Rdd1 Nb5 71. Rd3 Qc8 72. Kg2 Qb8 73. Re1 Kf5 74. Kh1 Rc1 75. Rd5+ Qe5 76. Rd8 Rh7 77. Rf1+ Ke4 78. Kg1 Qc5 79. Rd4+ Kxd4 80. Re1 Qc2 81. Rxc1 Kd5 82. Rb1 Qxb1+ 83. Kh2 Qg1+ 84. Kh3 e2

**Level 0, seed 3: unfinished at 290 plies**

1. a3 c6 2. e4 Qc7 3. Bc4 Qb6 4. d3 d5 5. Kf1 a5 6. Bh6 dxe4 7. Bd2 Qb3 8. Be1 Qa2 9. f4 Kd7 10. Nc3 Nf6 11. Ba6 Kd6 12. Bd2 g5 13. Be3 Qxb2 14. h3 Kd7 15. Nxe4 Nxa6 16. g4 Nd5 17. a4 Qb4 18. Bd4 Ke6 19. Qf3 Nf6 20. Rh2 Nd5 21. Nxg5+ Kd7 22. Kg2 Ra7 23. c4 Nb8 24. Qxd5+ Ke8 25. Rf1 Rg8 26. Be5 Bh6 27. Nxf7 Rf8 28. Bxb8 Bg5 29. Rb1 Qe1 30. Rh1 Rg8 31. Kf3 Qe6 32. Rh2 Qxf7 33. Qxg5 Be6 34. c5 Rg6 35. Rb6 Bxg4+ 36. Kg2 Qf8 37. d4 Re6 38. Rb4 Qg7 39. Rxb7 Re5 40. h4 Be2 41. Rh3 Qh8 42. Nf3 Kd8 43. Bxe5 Ra6 44. Kh1 Bd3 45. Kg2 Rb6 46. Ra7 Ra6 47. Qg3 Be4 48. Kf2 Bf5 49. Qh2 Be4 50. Rg3 Bd3 51. Ra8+ Rxa8 52. Bc7+ Kd7 53. Qg1 Be2 54. Qh1 Qd8 55. d5 e6 56. Kxe2 Kc8 57. d6 Qe8 58. Qh2 Qh5 59. Bb6 Qh6 60. Kf1 Qf6 61. Ke2 Kb8 62. Ba7+ Kb7 63. Kf1 Rf8 64. Ne5 Kc8 65. Qb2 Qg6 66. Qb6 Qg7 67. Nd7 Qg8 68. Qxa5 h6 69. Rxg8 Re8 70. Bb6 Rd8 71. Rg1 Kb7 72. Ne5 h5 73. Qb5 Kb8 74. Nxc6+ Kb7 75. Ba5+ Ka8 76. d7 Rc8 77. Qe2 Rc7 78. Qh2 Kb7 79. Qh1 Rxc6 80. Qf3 e5 81. Qg4 exf4 82. Qxh5 Ra6 83. Rg5 Ka7 84. Be1 Kb8 85. Qd1 Rd6 86. Qd3 Kc7 87. Qh7 Rxd7 88. Qe7 Rxe7 89. Rg6 Kb8 90. Rg3 Rc7 91. Bb4 Rb7 92. Ba5 Rb2 93. Rd3 Kb7 94. Rh3 Ra2 95. Bd2 Ra3 96. Rh2 Ka7 97. Be3 Kb8 98. Rb2+ Rb3 99. Rb1 Rxb1+ 100. Ke2 Ka7 101. Kd3 Rb2 102. Kc3 fxe3 103. Kd3 Rf2 104. Kc3 Rh2 105. Kd3 Rc2 106. Kxe3 Rh2 107. Kd4 Ka6 108. c6 Re2 109. Kd5 Ka5 110. Kd4 Re8 111. Kd3 Kb4 112. Kd4 Re5 113. Kd3 Re7 114. Kd4 Rc7 115. Kd5 Ka5 116. Kc5 Ka6 117. Kd4 Re7 118. Kc4 Rf7 119. Kb3 Rg7 120. Kb4 Rg5 121. c7 Kb6 122. a5+ Kc6 123. Ka4 Kd7 124. Ka3 Rd5 125. Kb3 Kc8 126. Ka3 Rb5 127. Ka2 Rf5 128. Ka1 Rf6 129. Kb2 Rf2+ 130. Kb1 Rb2+ 131. Kxb2 Kxc7 132. h5 Kc8 133. Kc1 Kb8 134. Kb2 Kc8 135. Kb1 Kd8 136. Kc2 Kc7 137. Kc3 Kb8 138. h6 Kc8 139. Kc2 Kd7 140. Kb1 Kc7 141. a6 Kb6 142. Kb2 Ka7 143. Ka2 Ka8 144. a7 Kb7 145. Ka3 Kc7

**Level 0, seed 4: DRAW: MATERIAL**

1. a3 g6 2. g4 c5 3. Nf3 f6 4. e4 e6 5. b4 a5 6. Nc3 Ne7 7. Bg2 Ng8 8. Qe2 Qb6 9. Ng5 c4 10. Nh3 Bh6 11. Na2 Qa6 12. Bf3 b5 13. Rb1 Be3 14. c3 Bxd2+ 15. Kxd2 h5 16. Kc2 d5 17. Bg5 Kd7 18. Qf1 d4 19. Qg1 Qd6 20. Kd2 dxc3+ 21. Kc1 Qf4+ 22. Nxf4 Kc6 23. Qg3 axb4 24. Re1 Kb7 25. Bh6 Ra7 26. g5 bxa3 27. Bg7 fxg5 28. Bd1 e5 29. Kc2 Kc7 30. Ne6+ Kc6 31. Nb4+ Kb7 32. Qxe5 a2 33. Qc7+ Ka8 34. Qf7 Ra4 35. Nxa2 Ra7 36. Qc7 Rb7 37. Rh1 Nh6 38. Qg3 g4 39. Rb4 Re7 40. Qxg4 Rf7 41. Qf4 Ng4 42. Qf6 Nxf2 43. Kc1 Nxd1 44. Qxg6 Nb2 45. h4 Rhf8 46. Nd4 Be6 47. Rg1 Bf5 48. Re1 Bc8 49. Rxb5 Na6 50. Kb1 Rh8 51. Be5 Rh6 52. Bf6 Nc5 53. Qxh5 Nca4 54. Be7 Bb7 55. e5 Rxe7 56. Rc1 Reh7 57. Qe2 Rg6 58. Nb3 Rh8 59. Qe1 Nd3 60. Qe2 Nxe5 61. Rd5 Rf8 62. Qg2 Bxd5 63. Na5 Ra6 64. Qh3 Nd3 65. Rc2 Rc6 66. Rg2 Ka7 67. Rg6 Ne1 68. Kc1 Rxg6 69. Qe3+ Rb6 70. Qe2 Rc8 71. Qg4 Ra8 72. Kd1 Re6 73. Qe2 Ng2 74. Qe5 Ka6 75. Qh5 Rh8 76. Kc1 Re1+ 77. Qd1 Be6 78. Nb4+ Kb5 79. Kb1 Kc5 80. Nxc4 Bd5 81. Ka2 Rxd1 82. Ka3 Rg1 83. Na5 Ne1 84. Nb3+ Bxb3 85. Na2 Rg7 86. h5 Kc4 87. Nxc3 Rb8 88. h6 Rd8 89. Nxa4 Rc7 90. Nb2+ Kb5 91. Nd3 Ra8+ 92. Kxb3 Rc4 93. Nf4 Ka6 94. Ka2 Rb8 95. Ne2 Ka5 96. Nd4 Rb7 97. Nb5 Rc6 98. Kb1 Rc5 99. Ka2 Rbxb5 100. Ka3 Nd3 101. Ka2 Rb2+ 102. Ka1 Ne5 103. h7 Rc3 104. h8=Q Rc4 105. Qh6 Rg2 106. Qh3 Rf2 107. Qh5 Rf1+ 108. Qd1 Kb4 109. Qxf1 Kb5 110. Qf4 Rc5 111. Kb2 Nf3 112. Qd6 Kb4 113. Qh6 Rc4 114. Qg6 Rc5 115. Qf5 Rc2+ 116. Kxc2 Nh4 117. Qf1 Ng2 118. Kd3 Ne3 119. Ke4 Kc5 120. Qd1 Kc6 121. Kf4 Nc2 122. Kg4 Kb5 123. Kh5 Ne3 124. Qe1 Nf5 125. Qe8+ Kc4 126. Qf7+ Kd3 127. Qg6 Kc3 128. Qe6 Kb2 129. Qd5 Kc2 130. Qb7 Nh4 131. Qb3+ Kxb3

**Level 0, seed 5: CHECKMATE**

1. e3 h5 2. Bc4 b5 3. b3 g6 4. Nh3 e5 5. Qf3 h4 6. Bd5 Nc6 7. g3 Nce7 8. Qh5 Nh6 9. Na3 Rh7 10. Qe2 f5 11. Qd1 Rf7 12. b4 e4 13. d3 d6 14. Bxa8 hxg3 15. Rf1 Nd5 16. Rg1 g5 17. c3 Rg7 18. Rb1 a6 19. Qb3 Rd7 20. Bxd5 Ng8 21. Bb2 Nf6 22. Ke2 c5 23. hxg3 Ra7 24. Rgf1 Bh6 25. Qc2 Ke7 26. bxc5 Qg8 27. Nxb5 Kd7 28. Rbe1 Nh7 29. Qc1 Qe8 30. Ba3 Ke7 31. Kd1 exd3 32. Nxd6 Qb5 33. Bf3 Nf8 34. Re2 Qxc5 35. Kd2 Bd7 36. Bb2 Qc6 37. Nf4 Kd8 38. Qd1 Qa4 39. Bg2 Qxa2 40. Bh1 Bc8 41. Qb1 Kc7 42. Qc2 Qa3 43. Kxd3 Qc5 44. Rd1 Qe5 45. Ne4 Bg7 46. Nc5 Qe8 47. Bg2 Bf6 48. Red2 Be5 49. c4 Bd6 50. Nb7 Nd7 51. Nh5 Nf8 52. Bc3 Bxg3 53. Qc1 Ng6 54. c5 Ra8 55. Nxg3 Ne5+ 56. Bxe5+ Qxe5 57. Rf1 Kb8 58. c6 Qd5+ 59. Kc2 Qc5+ 60. Kb1 Bd7 61. Nh5 Qa5 62. Rxd7 Kc8 63. Ng3 Qa1+ 64. Kxa1 a5 65. Be4 g4 66. c7 Ra7 67. Kb2 Rxb7+ 68. Bxb7+ Kxd7 69. Kc2 Ke8 70. Bh1 Kf7 71. e4 a4 72. Kb1 Kg6 73. Ka2 Kg7 74. Ka1 Kg8 75. c8=Q+ Kf7 76. f4 Kf6 77. e5+ Kg6 78. Rg1 a3 79. Bd5 a2 80. Be4 fxe4 81. Kxa2 Kf7 82. Q1c2 Ke7 83. Kb2 Kf7 84. Qf5+ Ke8 85. Kb1 Kd8 86. Qa2 e3 87. Qff7 e2 88. Qc7+ Kxc7 89. Qc2+ Kd8 90. Ka1 Ke7 91. Nf5+ Kd8 92. Qb1 Kc8 93. Qb7+ Kxb7 94. Nd4 Ka8 95. Rg3 Kb8 96. Rh3 Kb7 97. Rh5 e1=Q+ 98. Kb2 Qd2+ 99. Ka3 Ka8 100. Kb3 Qd1+ 101. Ka2 Qxd4 102. Rh3 Qf2+ 103. Kb1 Qg3 104. Rh4 Qg1+ 105. Kc2 Qc1+ 106. Kxc1 Kb8 107. e6 Ka7 108. Rh5 Kb7 109. f5 Kc7 110. Kc2 g3 111. Rh1 Kd8 112. Rh4 Ke8 113. Rf4 Kd8 114. Rh4 Kc7 115. Rb4 Kd8 116. Rb3 Kc8 117. Re3 Kb8 118. Kd1 Kc8 119. Ra3 Kc7 120. e7 Kc8 121. Ke2 g2 122. Rb3 g1=Q 123. Rb2 Qc1 124. Rb7 Qc6 125. Rb5 Qc5 126. Kd1 Qc4 127. Rb4 Qg4+ 128. Rxg4 Kd7 129. Re4 Kc8 130. Rh4 Kb8 131. Rh6 Kc8 132. Kd2 Kb8 133. Kc1 Kc8 134. Rh1 Kb7 135. Kd1 Kc6 136. Rh6+ Kb7 137. Rh7 Kb8 138. e8=Q#

**Level 1, seed 101: STALEMATE**

1. d4 d5 2. c4 c6 3. Nf3 Nf6 4. Nc3 dxc4 5. a4 Bf5 6. e4 Nxe4 7. Nxe4 Bxe4 8. Bxc4 Bxf3 9. gxf3 Qxd4 10. Qxd4 e5 11. Qxe5+ Be7 12. Qxe7+ Kxe7 13. Bxf7 Kxf7 14. b4 Kg8 15. h4 Nd7 16. Be3 a5 17. bxa5 Rxa5 18. O-O Rxa4 19. Rxa4 b5 20. Ra7 g5 21. Rxd7 gxh4 22. Rxh7 Rxh7 23. f4 h3 24. f3 h2+ 25. Kh1 b4 26. f5 b3 27. f4 b2 28. f6 b1=Q 29. Rxb1 c5 30. Bxc5 Kh8 31. Rb7 Rxb7 32. Kxh2 Rb2+ 33. Kh1 Ra2 34. f5 Rb2 35. f7 Ra2 36. f8=Q+ Kh7 37. f6 Rb2 38. f7 Ra2 39. Qd6 Kh8 40. f8=Q+ Kh7 41. Qf5+ Kh8 42. Bd4+ Kg8 43. Qe4 Rb2 44. Bxb2 Kf7 45. Bd4 Kg8 46. Qde5 Kf8 47. Q4d5

**Level 1, seed 102: DRAW: REPETITION**

1. e4 d5 2. exd5 Qxd5 3. Nc3 Qa5 4. d4 Nf6 5. Nf3 c6 6. a4 Qxc3+ 7. bxc3 e5 8. Nxe5 Nbd7 9. Nxd7 Bxd7 10. f4 a5 11. g4 Nxg4 12. Qxg4 Bxg4 13. h4 b5 14. Bxb5 cxb5 15. axb5 f5 16. Rxa5 Rxa5 17. Be3 Rxb5 18. O-O g5 19. fxg5 h5 20. gxh6 Bxh6 21. Bxh6 Rxh6 22. Rxf5 Bxf5 23. c4 Rxh4 24. cxb5 Rxd4 25. c4 Rxc4 26. b6 Rc2 27. b7 Kf8 28. b8=Q+ Bc8 29. Qxc8+ Rxc8 30. Kh1 Rc2 31. Kg1 Kg8 32. Kh1 Kh8 33. Kg1 Rb2 34. Kh1 Ra2 35. Kg1 Rb2 36. Kh1 Ra2 37. Kg1 Rb2

**Level 1, seed 103: STALEMATE**

1. Nf3 d5 2. g3 Nf6 3. Bg2 e6 4. O-O Be7 5. d3 O-O 6. e4 Nxe4 7. dxe4 dxe4 8. Qxd8 Rxd8 9. Nbd2 Rxd2 10. Bxd2 exf3 11. Bxf3 Nc6 12. Bxc6 bxc6 13. a4 a5 14. Bxa5 Rxa5 15. b4 Rxa4 16. Rxa4 Bxb4 17. Rxb4 f5 18. c4 g5 19. f4 gxf4 20. gxf4 h5 21. h4 c5 22. Rb7 Bxb7 23. Re1 Bd5 24. cxd5 exd5 25. Re7 c4 26. Rxc7 c3 27. Rxc3 d4 28. Rc7 Kh8 29. Kh1 d3 30. Rb7 d2 31. Ra7 d1=Q+ 32. Kh2 Qd4 33. Kh1 Qxa7 34. Kh2 Qd4 35. Kh1 Qxf4 36. Kg1 Qxh4 37. Kf1 Qe4 38. Kg1 f4 39. Kf1 f3 40. Kg1 f2+ 41. Kxf2 h4 42. Kg1 h3 43. Kf1 h2 44. Kf2 h1=Q 45. Kg3 Qhf3+ 46. Kh2 Qfe3

**Level 1, seed 104: STALEMATE**

1. Nf3 d5 2. g3 Nf6 3. Bg2 e6 4. O-O Be7 5. d3 O-O 6. e4 Nxe4 7. dxe4 dxe4 8. Qxd8 Rxd8 9. Nbd2 Rxd2 10. Bxd2 exf3 11. Bxf3 Nc6 12. Bxc6 bxc6 13. a4 a5 14. Bxa5 Rxa5 15. b4 Rxa4 16. Rxa4 Bxb4 17. Rxb4 f5 18. c4 g5 19. f4 gxf4 20. gxf4 h5 21. h4 c5 22. Rb7 Bxb7 23. Re1 Bd5 24. cxd5 exd5 25. Re7 c4 26. Rxc7 c3 27. Rxc3 d4 28. Rc7 Kh8 29. Kh1 d3 30. Rb7 d2 31. Ra7 d1=Q+ 32. Kh2 Qd4 33. Kh1 Qxa7 34. Kh2 Qd4 35. Kh1 Qxf4 36. Kg1 Qxh4 37. Kf1 Qe4 38. Kg1 f4 39. Kf1 f3 40. Kg1 f2+ 41. Kxf2 h4 42. Kg1 h3 43. Kf1 h2 44. Kf2 h1=Q 45. Kg3 Qhf3+ 46. Kh2 Qfe3

**Level 1, seed 105: DRAW: MATERIAL**

1. c4 e5 2. Nc3 Nf6 3. Nf3 Nc6 4. g3 d5 5. cxd5 Nxd5 6. Nxd5 Qxd5 7. Nxe5 Qxh1 8. Nxc6 Qxf1+ 9. Kxf1 bxc6 10. d4 a5 11. e4 f5 12. exf5 Bxf5 13. a4 g5 14. Bxg5 h5 15. Qxh5+ Rxh5 16. b4 Rxg5 17. bxa5 Rxa5 18. f4 Rxa4 19. fxg5 Rxa1+ 20. Kg2 Ra2+ 21. Kh1 Rxh2+ 22. Kxh2 Bd6 23. Kh1 Bxg3 24. d5 cxd5 25. g6 Bxg6 26. Kg1 c5 27. Kh1 Be5 28. Kg1 Be4 29. Kf1 c4 30. Kg1 c3 31. Kf1 c2 32. Kg1 c1=Q+ 33. Kf2 Qe3+ 34. Kxe3 d4+ 35. Kxe4 Kf8 36. Kxe5 Kg8 37. Kxd4

**Level 2, seed 201: DRAW: REPETITION**

1. e4 c6 2. d4 d5 3. Nc3 dxe4 4. Nxe4 Bf5 5. Ng3 Bg6 6. N1e2 Nd7 7. a4 e5 8. c4 Ngf6 9. f4 a5 10. fxe5 Ne4 11. Nxe4 Bxe4 12. h4 b5 13. axb5 cxb5 14. cxb5 g5 15. Bxg5 f6 16. exf6 Nxf6 17. h5 Bd6 18. d5 Bxd5 19. Nd4 O-O 20. b3 a4 21. bxa4 Kh8 22. a5 Rxa5 23. Rxa5 Qxa5+ 24. Qd2 Qxd2+ 25. Bxd2 Ne4 26. g4 Nxd2 27. Rg1 Nxf1 28. Rxf1 Rxf1+ 29. Kxf1 h6 30. b6 Be5 31. Nf5 Bf4 32. Nd4 Be5 33. Nf5 Bf4 34. Nd4 Be5

**Level 2, seed 202: CHECKMATE**

1. d4 d5 2. c4 e6 3. Nc3 Nf6 4. Bg5 Be7 5. e3 O-O 6. cxd5 Nxd5 7. Nf3 Bxg5 8. Nxg5 Qxg5 9. Nxd5 exd5 10. a4 Nc6 11. f4 Qf5 12. g4 Qxg4 13. h4 a5 14. Bd3 f5 15. Qxg4 fxg4 16. O-O h5 17. b3 Be6 18. f5 Bxf5 19. Rxf5 Rxf5 20. Bxf5 g3 21. Kh1 b6 22. Rb1 Kh8 23. b4 axb4 24. Ra1 b3 25. a5 bxa5 26. Rb1 a4 27. Ra1 b2 28. Rb1 a3 29. Bd3 Nb4 30. Bf5 c6 31. e4 Nd3 32. e5 Nf4 33. e6 g2+ 34. Kg1 g6 35. Bc2 Nxe6 36. Kxg2 Nxd4 37. Bxg6 c5 38. Bxh5 c4 39. Kh1 c3 40. Bg4 a2 41. Rxb2 a1=Q+ 42. Rb1 Qxb1+ 43. Kh2 Qe4 44. Kh3 Ra2 45. h5 c2 46. h6 c1=Q 47. h7 Qxh7+ 48. Kg3 Qcc7#

**Level 2, seed 203: CHECKMATE**

1. e4 c5 2. Nf3 d6 3. d4 cxd4 4. Nxd4 Nf6 5. Nc3 a6 6. a4 e5 7. Nf5 Nc6 8. Nxd6+ Bxd6 9. f4 exf4 10. h4 b5 11. axb5 Nb4 12. bxa6 Bxa6 13. Bxa6 Rxa6 14. Rxa6 Nxa6 15. O-O Nc5 16. Bxf4 Nfxe4 17. Bxd6 Qxd6 18. Qxd6 Nxd6 19. b4 Nce4 20. Nxe4 Nxe4 21. c4 g5 22. hxg5 Nxg5 23. g4 h5 24. gxh5 Rxh5 25. b5 Ne4 26. b6 f5 27. b7 Rh2 28. b8=Q+ Kf7 29. Qxh2 Kg6 30. Qe5 Kg5 31. Rxf5+ Kh6 32. Qxe4 Kh7 33. Rf7+ Kh8 34. Qa8#

**Level 2, seed 204: DRAW: REPETITION**

1. e4 c5 2. Nf3 Nc6 3. d4 cxd4 4. Nxd4 Nf6 5. Nc3 e5 6. Nxc6 bxc6 7. a4 d5 8. exd5 cxd5 9. Nxd5 Nxd5 10. c4 Nf4 11. Qxd8+ Kxd8 12. h4 a5 13. Be3 f5 14. b3 h5 15. f3 Be6 16. g4 fxg4 17. fxg4 hxg4 18. h5 Rxh5 19. Rxh5 Nxh5 20. Bd3 Nf4 21. Be4 Ra6 22. Kf1 g5 23. Kg1 Bd6 24. Kh1 g3 25. Rb1 g2+ 26. Bxg2 Nxg2 27. Kxg2 g4 28. Kh1 g3 29. c5 Be7 30. b4 axb4 31. Rxb4 Kc8 32. Re4 Bf6 33. Rb4 Bd5+ 34. Kg1 g2 35. Rg4 Kb8 36. Rb4+ Ka8 37. Rg4 Ra5 38. Rb4 Ra6 39. Rg4 Ra5 40. Rb4 Ra6

**Level 2, seed 205: CHECKMATE**

1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. c3 Nf6 5. d4 exd4 6. cxd4 Nxd4 7. Nxd4 Nxe4 8. Nc3 d5 9. Nxd5 a5 10. a4 f5 11. b4 axb4 12. f4 g5 13. fxg5 Nxg5 14. g4 fxg4 15. Be3 h5 16. O-O Ne4 17. a5 h4 18. Qd3 Nd6 19. Kh1 Nxc4 20. Qxc4 b6 21. Nxb4 Bxd4 22. Qf7#

