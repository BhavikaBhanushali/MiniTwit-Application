INSERT INTO user (username, email, pw_hash)
VALUES
('markie', 'markie@twit.com', 'pbkdf2:sha256:50000$Q3rOrefL$0b0e20dab9072f9dd0bb501ff7400ec9a2087d65f0fa5a189d348cb39e89116b'),
('john', 'john@twit.com', 'pbkdf2:sha256:50000$Q3rOrefL$0b0e20dab9072f9dd0bb501ff7400ec9a2087d65f0fa5a189d348cb39e89116b'),
('nicholas', 'nicholas@twit.com', 'pbkdf2:sha256:50000$Q3rOrefL$0b0e20dab9072f9dd0bb501ff7400ec9a2087d65f0fa5a189d348cb39e89116b'),
('ryan', 'ryan@twit.com', 'pbkdf2:sha256:50000$Q3rOrefL$0b0e20dab9072f9dd0bb501ff7400ec9a2087d65f0fa5a189d348cb39e89116b'),
('brain', 'brain@twit.com', 'pbkdf2:sha256:50000$Q3rOrefL$0b0e20dab9072f9dd0bb501ff7400ec9a2087d65f0fa5a189d348cb39e89116b'),
('jessica', 'jessica@twit.com', 'pbkdf2:sha256:50000$Q3rOrefL$0b0e20dab9072f9dd0bb501ff7400ec9a2087d65f0fa5a189d348cb39e89116b'),
('methew', 'methew@twit.com', 'pbkdf2:sha256:50000$Q3rOrefL$0b0e20dab9072f9dd0bb501ff7400ec9a2087d65f0fa5a189d348cb39e89116b'),
('jacob', 'jacob@twit.com', 'pbkdf2:sha256:50000$Q3rOrefL$0b0e20dab9072f9dd0bb501ff7400ec9a2087d65f0fa5a189d348cb39e89116b'),
('lauren', 'lauren@twit.com', 'pbkdf2:sha256:50000$Q3rOrefL$0b0e20dab9072f9dd0bb501ff7400ec9a2087d65f0fa5a189d348cb39e89116b'),
('shawn', 'shawn@twit.com', 'pbkdf2:sha256:50000$Q3rOrefL$0b0e20dab9072f9dd0bb501ff7400ec9a2087d65f0fa5a189d348cb39e89116b'),
('andrwe', 'andrwe@twit.com', 'pbkdf2:sha256:50000$Q3rOrefL$0b0e20dab9072f9dd0bb501ff7400ec9a2087d65f0fa5a189d348cb39e89116b'),
('laurance', 'laurance@twit.com', 'pbkdf2:sha256:50000$Q3rOrefL$0b0e20dab9072f9dd0bb501ff7400ec9a2087d65f0fa5a189d348cb39e89116b'),
('kevin', 'kevin@twit.com', 'pbkdf2:sha256:50000$Q3rOrefL$0b0e20dab9072f9dd0bb501ff7400ec9a2087d65f0fa5a189d348cb39e89116b'),
('cavan', 'cavan@twit.com', 'pbkdf2:sha256:50000$Q3rOrefL$0b0e20dab9072f9dd0bb501ff7400ec9a2087d65f0fa5a189d348cb39e89116b'),
('glen', 'glen@twit.com', 'pbkdf2:sha256:50000$Q3rOrefL$0b0e20dab9072f9dd0bb501ff7400ec9a2087d65f0fa5a189d348cb39e89116b'),
('obama', 'obama@twit.com', 'pbkdf2:sha256:50000$Q3rOrefL$0b0e20dab9072f9dd0bb501ff7400ec9a2087d65f0fa5a189d348cb39e89116b'),
('cong', 'cong@twit.com', 'pbkdf2:sha256:50000$Q3rOrefL$0b0e20dab9072f9dd0bb501ff7400ec9a2087d65f0fa5a189d348cb39e89116b'),
('lee', 'lee@twit.com', 'pbkdf2:sha256:50000$Q3rOrefL$0b0e20dab9072f9dd0bb501ff7400ec9a2087d65f0fa5a189d348cb39e89116b');



INSERT INTO follower (who_id, whom_id)
VALUES
	(1, 12),
	(2, 11),
	(13, 14),
	(8, 3),
	(1, 5),
	(5, 18),
	(15, 14),
	(5, 15),
	(4, 12),
	(13, 11),
	(11, 2),
	(18, 7),
	(11, 2),
	(10, 3),
	(3, 5),
	(15, 11),
	(1, 19),
	(16, 11),
	(19, 8),
	(17, 3);

INSERT INTO message (author_id, text, pub_date)
VALUES
	(1, 'This is message from user 1', 1518286938),
	(2, 'User 2 Message is working', 1518286938),
	(3, 'Hello World', 1518359178),
	(4, 'Blue Sky', 1518359178),
	(5, 'Cal State Fullerton', 1518286938),
	(6, 'Test message', 1518286938),
	(7, 'Hi All', 1518207438),
	(8, 'Rock on', 1518286938),
	(9, 'Twitter', 1517887392),
	(10, 'Mini Twit', 1517887392),
	(11, 'Love the nature', 1517988089),
	(12, 'I am here', 1517887392),
	(13, 'Watching Black Panther', 1517887392),
	(14, 'Tuffy Titants', 1517887392),
	(15, 'The secrates', 1517887392),
	(16, 'Love the nature', 1517887392),
	(17, 'Hello World', 1518286938),
	(18, 'Good Morning', 1517719341),
	(19, 'Spring', 1517719341),
	(20, 'ASI', 1517539404);
