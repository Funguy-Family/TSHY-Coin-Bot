USE [FunguyFamilyDB]
GO
/****** Object:  Table [dbo].[AirdropMasterTbl]    Script Date: 1/23/2022 4:59:36 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[AirdropMasterTbl](
	[AirdropID] [int] IDENTITY(1,1) NOT NULL,
	[AirdropYear] [int] NOT NULL,
	[AirdropMonth] [int] NOT NULL,
	[AirdropName] [varchar](100) NOT NULL,
	[AirdropIsCurrent] [bit] NOT NULL,
 CONSTRAINT [PK_AirdropMasterTbl] PRIMARY KEY CLUSTERED 
(
	[AirdropID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[AirdropSignInTbl]    Script Date: 1/23/2022 4:59:37 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[AirdropSignInTbl](
	[AirdropID] [int] NOT NULL,
	[DiscordUserID] [bigint] NOT NULL,
	[TshyCoin] [int] NOT NULL,
	[SignInUTCTime] [datetime] NOT NULL,
 CONSTRAINT [PK_AirdropSignInTbl] PRIMARY KEY CLUSTERED 
(
	[AirdropID] ASC,
	[DiscordUserID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[FunguyAdminUserTbl]    Script Date: 1/23/2022 4:59:37 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[FunguyAdminUserTbl](
	[DiscordUserID] [bigint] NOT NULL,
 CONSTRAINT [PK_FunguyAdminUserTbl] PRIMARY KEY CLUSTERED 
(
	[DiscordUserID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[FunguyUserTbl]    Script Date: 1/23/2022 4:59:37 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[FunguyUserTbl](
	[DiscordUserID] [bigint] NOT NULL,
	[DiscordUserName] [varchar](100) NOT NULL,
	[DiscordUserTag] [int] NOT NULL,
	[WalletAddress] [varchar](100) NOT NULL,
	[NumberOfFunguysOwned] [int] NOT NULL,
	[DateOfOldestFunguyOwned] [date] NOT NULL,
 CONSTRAINT [PK_FunguyUserTbl] PRIMARY KEY CLUSTERED 
(
	[DiscordUserID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
ALTER TABLE [dbo].[AirdropSignInTbl]  WITH CHECK ADD  CONSTRAINT [FK_AirdropSignInTbl_AirdropMasterTbl] FOREIGN KEY([AirdropID])
REFERENCES [dbo].[AirdropMasterTbl] ([AirdropID])
GO
ALTER TABLE [dbo].[AirdropSignInTbl] CHECK CONSTRAINT [FK_AirdropSignInTbl_AirdropMasterTbl]
GO
ALTER TABLE [dbo].[AirdropSignInTbl]  WITH CHECK ADD  CONSTRAINT [FK_AirdropSignInTbl_FunguyUserTbl] FOREIGN KEY([DiscordUserID])
REFERENCES [dbo].[FunguyUserTbl] ([DiscordUserID])
GO
ALTER TABLE [dbo].[AirdropSignInTbl] CHECK CONSTRAINT [FK_AirdropSignInTbl_FunguyUserTbl]
GO
/****** Object:  StoredProcedure [dbo].[CalculateTSHYCoinProc]    Script Date: 1/23/2022 4:59:37 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

-- =============================================
-- Author:		Pringles
-- Create date: 1/22/2022
-- Description:	Just a script to calculate TSHY coins
-- =============================================
CREATE PROCEDURE [dbo].[CalculateTSHYCoinProc]
	@Data nvarchar(max)
--'[
--	{ 
--		"AirdropName" : "January 2022 - Tuschay Coin ($TSHY) Airdrop",
--		"DiscordUserID": "3"
--	}
--]'
AS
BEGIN

----------
-- Parse Data
----------

CREATE TABLE #TempCurrentAirdropSignInTbl(
	[AirdropName] VARCHAR(100),
	[DiscordUserID] BIGINT
)

INSERT INTO #TempCurrentAirdropSignInTbl(
	[AirdropName],
	[DiscordUserID]
)
SELECT 
	AirdropName,
	DiscordUserID
FROM OPENJSON(@Data)
WITH (	
	AirdropName VARCHAR(100),
	DiscordUserID BIGINT
)

DECLARE @AirDriopID INT
DECLARE @Month DATE
SELECT
	@AirDriopID = A.AirdropID,
	@Month =    CAST(
      CAST(A.AirdropYear AS VARCHAR(4)) +
      RIGHT('0' + CAST(A.AirdropMonth AS VARCHAR(2)), 2) +
      RIGHT('0' + CAST(1 AS VARCHAR(2)), 2) 
   AS DATE)
FROM [dbo].[AirdropMasterTbl] A
INNER JOIN #TempCurrentAirdropSignInTbl B ON
	A.AirdropName = B.AirdropName

----------
-- Error check
----------
DECLARE @ErrorMsg VARCHAR(1000)

IF @AirDriopID IS NULL
BEGIN
	SET @ErrorMsg = 'Did not find Airdrop form.'
	GOTO ErrorCode
END

IF NOT EXISTS(
	SELECT
		1
	FROM #TempCurrentAirdropSignInTbl A
	INNER JOIN [dbo].[FunguyAdminUserTbl] B ON
		A.DiscordUserID = B.DiscordUserID
)
BEGIN
	SET @ErrorMsg = 'User is not an admin.'
	GOTO ErrorCode
END
---------
-- Add new user
---------

UPDATE A
SET
	A.[TshyCoin] = (100 * B.[NumberOfFunguysOwned])*(1 + (DATEDIFF(month, B.DateOfOldestFunguyOwned, @Month) + 1)/10.0)
FROM [AirdropSignInTbl] A
-----------------------------------------------
INNER JOIN [dbo].[FunguyUserTbl] B ON
-----------------------------------------------
	A.DiscordUserID = B.DiscordUserID
WHERE
	A.AirdropID = @AirDriopID

ExitCode:
	SELECT 
		1 AS STATUS,
		'' AS ErrorMsg
	FROM #TempCurrentAirdropSignInTbl
	FOR JSON AUTO
	RETURN 1
ErrorCode:
	SELECT 
		0 AS STATUS,
		@ErrorMsg AS ErrorMsg
	FROM #TempCurrentAirdropSignInTbl
	FOR JSON AUTO

	RETURN 0

END

GO
/****** Object:  StoredProcedure [dbo].[InsertAirdropSignInTblProc]    Script Date: 1/23/2022 4:59:37 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

-- =============================================
-- Author:		Pringles
-- Create date: 1/22/2022
-- Description:	Just a script to create a new funguy user
-- =============================================
CREATE PROCEDURE [dbo].[InsertAirdropSignInTblProc]
	@Data nvarchar(max)
--'[
--	{ 
--		"DiscordUserID" : "2",
--	}
--]'
AS
BEGIN

----------
-- Parse Data
----------
DECLARE @AirDriopID INT
SELECT
	@AirDriopID = AirdropID
FROM [dbo].[AirdropMasterTbl]
WHERE
	AirdropIsCurrent = 1

CREATE TABLE #TempCurrentAirdropSignInTbl(
	[AirDropID] INT,
	[DiscordUserID] BIGINT,
)

INSERT INTO #TempCurrentAirdropSignInTbl(
	[AirDropID],
	[DiscordUserID]
)
SELECT 
	@AirDriopID, 
	DiscordUserID
FROM OPENJSON(@Data)
WITH (	
	[DiscordUserID] BIGINT
)

----------
-- Error check
----------
DECLARE @ErrorMsg VARCHAR(1000)

IF NOT EXISTS(
	SELECT 
		1
	FROM [dbo].[FunguyUserTbl] A
	-----------------------------
	INNER JOIN #TempCurrentAirdropSignInTbl B ON
	-----------------------------
		A.DiscordUserID = B.DiscordUserID
)
BEGIN
	SET @ErrorMsg = 'User not found.'
	GOTO ErrorCode
END

IF EXISTS(
	SELECT 
		1
	FROM [dbo].[AirdropSignInTbl] A
	-----------------------------
	INNER JOIN #TempCurrentAirdropSignInTbl B ON
	-----------------------------
			A.DiscordUserID = B.DiscordUserID
		AND	A.AirdropID = @AirDriopID
)
BEGIN
	SET @ErrorMsg = 'User already has signed in.'
	GOTO ErrorCode
END

---------
-- Add new user
---------
DECLARE @NumberOfFunguysOwned INT
DECLARE @Month INT

SELECT
	@NumberOfFunguysOwned = NumberOfFunguysOwned,
	@Month = DATEDIFF(month, DateOfOldestFunguyOwned, GETUTCDATE()) + 1
FROM [dbo].[FunguyUserTbl] A
-----------------------------------------------
INNER JOIN #TempCurrentAirdropSignInTbl B ON
-----------------------------------------------
	A.DiscordUserID = B.DiscordUserID

INSERT INTO [AirdropSignInTbl](
	[AirdropID],
	[DiscordUserID],
	[TshyCoin],
	[SignInUTCTime]
)
SELECT
	@AirDriopID,
	DiscordUserID,
	(100 * @NumberOfFunguysOwned)*(1 + @Month/10.0),
	GETUTCDATE()
FROM #TempCurrentAirdropSignInTbl


ExitCode:
	SELECT 
		1 AS STATUS,
		'' AS ErrorMsg
	FROM #TempCurrentAirdropSignInTbl
	FOR JSON AUTO
	RETURN 1
ErrorCode:
	SELECT 
		0 AS STATUS,
		@ErrorMsg AS ErrorMsg
	FROM #TempCurrentAirdropSignInTbl
	FOR JSON AUTO

	RETURN 0

END

GO
/****** Object:  StoredProcedure [dbo].[InsertFunguyUserProc]    Script Date: 1/23/2022 4:59:37 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

-- =============================================
-- Author:		Pringles
-- Create date: 1/22/2022
-- Description:	Just a script to create a new funguy user
-- =============================================
CREATE PROCEDURE [dbo].[InsertFunguyUserProc]
	@Data nvarchar(max)
--'[
--	{ 
--		"DiscordUserID" : "2",
--		"DiscordUserName": "John",
--		"DiscordUserTag": "0001",
--		"WalletAddress": "awrfafaw",
--		"NumberOfFunguysOwned": "2",
--		"DateOfOldestFunguyOwned": "2021-12-21"
--	}
--]'
AS
BEGIN

----------
-- Parse Data
----------
CREATE TABLE #TempCurrentFunguyUserTbl(
	[DiscordUserID] BIGINT,
	[DiscordUserName] VARCHAR(100),
	[DiscordUserTag] INT,
	[WalletAddress] VARCHAR(100),
	[NumberOfFunguysOwned] INT,
	[DateOfOldestFunguyOwned] DATE
)

INSERT INTO #TempCurrentFunguyUserTbl(
	[DiscordUserID],
	[DiscordUserName],
	[DiscordUserTag],
	[WalletAddress],
	[NumberOfFunguysOwned],
	[DateOfOldestFunguyOwned]
)
SELECT 
	DiscordUserID, 
	DiscordUserName,
	DiscordUserTag,
	WalletAddress,
	NumberOfFunguysOwned,
	DateOfOldestFunguyOwned
FROM OPENJSON(@Data)
WITH (	
	[DiscordUserID] BIGINT,
	[DiscordUserName] VARCHAR(100),
	[DiscordUserTag] INT,
	[WalletAddress] VARCHAR(100),
	[NumberOfFunguysOwned] INT,
	[DateOfOldestFunguyOwned] DATE
)

----------
-- Error check
----------
DECLARE @ErrorMsg VARCHAR(1000)

IF EXISTS(
	SELECT 
		1
	FROM [dbo].[FunguyUserTbl] A
	-----------------------------
	INNER JOIN #TempCurrentFunguyUserTbl B ON
	-----------------------------
		A.DiscordUserID = B.DiscordUserID
)
BEGIN
	SET @ErrorMsg = 'User already exists.'
	GOTO ErrorCode
END

IF EXISTS(
	SELECT 
		1
	FROM [dbo].[FunguyUserTbl] A
	-----------------------------
	INNER JOIN #TempCurrentFunguyUserTbl B ON
	-----------------------------
		A.WalletAddress = B.WalletAddress
)
BEGIN
	SET @ErrorMsg = 'Wallet already being used by another user.'
	GOTO ErrorCode
END

INSERT INTO [FunguyUserTbl](
	[DiscordUserID],
	[DiscordUserName],
	[DiscordUserTag],
	[WalletAddress],
	[NumberOfFunguysOwned],
	[DateOfOldestFunguyOwned]
)
SELECT
	[DiscordUserID],
	[DiscordUserName],
	[DiscordUserTag],
	[WalletAddress],
	[NumberOfFunguysOwned],
	[DateOfOldestFunguyOwned]
FROM #TempCurrentFunguyUserTbl


ExitCode:
	SELECT 
		1 AS STATUS,
		'' AS ErrorMsg
	FROM #TempCurrentFunguyUserTbl
	FOR JSON AUTO
	RETURN 1
ErrorCode:
	SELECT 
		0 AS STATUS,
		@ErrorMsg AS ErrorMsg
	FROM #TempCurrentFunguyUserTbl
	FOR JSON AUTO

	RETURN 0

END

GO
/****** Object:  StoredProcedure [dbo].[PopulateAirDropMasterTblProc]    Script Date: 1/23/2022 4:59:37 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

-- =============================================
-- Author:		Pringles
-- Create date: 1/22/2022
-- Description:	Just a script to populate the airdrop masterTbl.
-- =============================================
CREATE PROCEDURE [dbo].[PopulateAirDropMasterTblProc]

AS
BEGIN
	CREATE TABLE #TempMonthTbl(
		MonthNumber int,
		MonthLongName varchar(50)
	)

	INSERT INTO #TempMonthTbl(
		MonthNumber,
		MonthLongName
	)
	VALUES
		(1, 'January'),
		(2, 'February'),
		(3, 'March'),
		(4, 'April'),
		(5, 'May'),
		(6, 'June'),
		(7, 'July'),
		(8, 'August'),
		(9, 'September'),
		(10, 'October'),
		(11, 'November'),
		(12, 'December')

	CREATE TABLE #TempYearTbl(
		YearhNumber int
	)

	INSERT INTO #TempYearTbl(
		YearhNumber
	)
	VALUES
		(2022),
		(2023),
		(2024),
		(2025),
		(2026),
		(2027),
		(2028),
		(2029),
		(2030)

	INSERT INTO [dbo].[AirdropMasterTbl](
		AirdropYear,
		AirdropMonth,
		AirDropName,
		AirdropIsCurrent
	)
	SELECT 
		#TempYearTbl.YearhNumber,
		#TempMonthTbl.MonthNumber,
		#TempMonthTbl.MonthLongName + ' ' + CAST(#TempYearTbl.YearhNumber AS VARCHAR(5)) + ' - Tuschay Coin ($TSHY) Airdrop',
		0
	FROM #TempMonthTbl
	CROSS JOIN #TempYearTbl

END

GO
/****** Object:  StoredProcedure [dbo].[UpdateAirDropMasterTblIsCurrentProc]    Script Date: 1/23/2022 4:59:37 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

-- =============================================
-- Author:		Pringles
-- Create date: 1/22/2022
-- Description:	Just a script to update current AirDrop, SQL Agent will call it
-- =============================================
CREATE PROCEDURE [dbo].[UpdateAirDropMasterTblIsCurrentProc]
AS
BEGIN

	DECLARE @CurrentDate DATE = GETDATE()
	DECLARE @LastDate Date = DATEADD(DAY,-1,@CurrentDate)

	UPDATE [dbo].[AirdropMasterTbl]
	SET
		AirdropIsCurrent = 1
	WHERE
			AirDropMonth = MONTH(@CurrentDate)
		AND AirdropYear =  YEAR(@CurrentDate)

	UPDATE [dbo].[AirdropMasterTbl]
	SET
		AirdropIsCurrent = 0
	WHERE
			AirDropMonth = MONTH(@LastDate)
		AND AirdropYear =  YEAR(@LastDate)
END

GO
/****** Object:  StoredProcedure [dbo].[UpdateFunguyUserProc]    Script Date: 1/23/2022 4:59:37 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

-- =============================================
-- Author:		Pringles
-- Create date: 1/23/2022
-- Description:	Just a script to Update a new funguy user
-- =============================================
CREATE PROCEDURE [dbo].[UpdateFunguyUserProc]
	@Data nvarchar(max)
--'[
--	{ 
--		"DiscordUserID" : "2",
--		"DiscordUserName": "John",
--		"DiscordUserTag": "0001",
--		"WalletAddress": "awrfafaw",
--		"NumberOfFunguysOwned": "2",
--		"IsItAddition": "1",
--		"DateOfOldestFunguyOwned": "2021-12-21"
--	}
--]'
AS
BEGIN

----------
-- Parse Data
----------
CREATE TABLE #TempCurrentFunguyUserTbl(
	[DiscordUserID] BIGINT,
	[DiscordUserName] VARCHAR(100),
	[DiscordUserTag] INT,
	[WalletAddress] VARCHAR(100),
	[NumberOfFunguysOwned] INT,
	[IsItAddition] BIT,
	[DateOfOldestFunguyOwned] DATE
)

INSERT INTO #TempCurrentFunguyUserTbl(
	[DiscordUserID],
	[DiscordUserName],
	[DiscordUserTag],
	[WalletAddress],
	[NumberOfFunguysOwned],
	[IsItAddition],
	[DateOfOldestFunguyOwned]
)
SELECT 
	DiscordUserID, 
	DiscordUserName,
	DiscordUserTag,
	WalletAddress,
	NumberOfFunguysOwned,
	IsItAddition,
	DateOfOldestFunguyOwned
FROM OPENJSON(@Data)
WITH (	
	[DiscordUserID] BIGINT,
	[DiscordUserName] VARCHAR(100),
	[DiscordUserTag] INT,
	[WalletAddress] VARCHAR(100),
	[NumberOfFunguysOwned] INT,
	[IsItAddition] BIT,
	[DateOfOldestFunguyOwned] DATE
)

----------
-- Error check
----------
DECLARE @ErrorMsg VARCHAR(1000)

IF NOT EXISTS(
	SELECT 
		1
	FROM [dbo].[FunguyUserTbl] A
	-----------------------------
	INNER JOIN #TempCurrentFunguyUserTbl B ON
	-----------------------------
		A.DiscordUserID = B.DiscordUserID
)
BEGIN
	SET @ErrorMsg = 'User not found.'
	GOTO ErrorCode
END

IF EXISTS(
	SELECT 
		1
	FROM [dbo].[FunguyUserTbl] A
	-----------------------------
	INNER JOIN #TempCurrentFunguyUserTbl B ON
	-----------------------------
			A.WalletAddress = B.WalletAddress
		AND A.DiscordUserID != B.DiscordUserID
)
BEGIN
	SET @ErrorMsg = 'Wallet Address is being used by another user.'
	GOTO ErrorCode
END

----------
-- Update 
----------
UPDATE A
SET
	A.[DiscordUserName] = B.[DiscordUserName],
	A.[DiscordUserTag] = B.[DiscordUserTag],
	A.[WalletAddress] = ISNULL(B.[WalletAddress], A.[WalletAddress]),
	A.[NumberOfFunguysOwned] = 
		CASE 
			WHEN B.[NumberOfFunguysOwned] IS NULL THEN A.[NumberOfFunguysOwned]
			WHEN B.[IsItAddition] = 1 THEN A.[NumberOfFunguysOwned] + B.[NumberOfFunguysOwned]
			WHEN B.[IsItAddition] = 0 THEN A.[NumberOfFunguysOwned] - B.[NumberOfFunguysOwned]
			WHEN B.[IsItAddition] IS NULL THEN B.[NumberOfFunguysOwned]
		END,
	A.[DateOfOldestFunguyOwned] = ISNULL(B.[DateOfOldestFunguyOwned], A.[DateOfOldestFunguyOwned])
FROM  [dbo].[FunguyUserTbl] A
-----------------------------
INNER JOIN #TempCurrentFunguyUserTbl B ON
-----------------------------
	A.DiscordUserID = B.DiscordUserID

ExitCode:
	SELECT 
		1 AS STATUS,
		'' AS ErrorMsg
	FROM #TempCurrentFunguyUserTbl
	FOR JSON AUTO
	RETURN 1
ErrorCode:
	SELECT 
		0 AS STATUS,
		@ErrorMsg AS ErrorMsg
	FROM #TempCurrentFunguyUserTbl
	FOR JSON AUTO

	RETURN 0

END

GO
/****** Object:  StoredProcedure [dbo].[ViewFunguyUserProc]    Script Date: 1/23/2022 4:59:37 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

-- =============================================
-- Author:		Pringles
-- Create date: 1/22/2022
-- Description:	Just a script to calculate TSHY coins
-- =============================================
CREATE PROCEDURE [dbo].[ViewFunguyUserProc]
	@Data nvarchar(max)
--'[
--	{ 
--		"DiscordUserID" : "2"
--	}
--]'
AS
BEGIN

----------
-- Parse Data
----------

CREATE TABLE #TempFunguyUserTbl(
	[DiscordUserID] BIGINT
)

INSERT INTO #TempFunguyUserTbl(
	[DiscordUserID]
)
SELECT 
	DiscordUserID
FROM OPENJSON(@Data)
WITH (	
	DiscordUserID BIGINT
)

----------
-- Error check
----------
DECLARE @ErrorMsg VARCHAR(1000)

IF NOT EXISTS(
	SELECT
		1
	FROM #TempFunguyUserTbl A 
	INNER JOIN [dbo].[FunguyUserTbl] B ON
		A.DiscordUserID = B.DiscordUserID
)
BEGIN
	SET @ErrorMsg = 'User was not found.'
	GOTO ErrorCode
END


ExitCode:
	SELECT 
		1 AS STATUS,
		'' AS ErrorMsg,
		B.WalletAddress,
		B.[NumberOfFunguysOwned],
		B.[DateOfOldestFunguyOwned]
	FROM #TempFunguyUserTbl A 
	INNER JOIN [dbo].[FunguyUserTbl] B ON
		A.DiscordUserID = B.DiscordUserID
	FOR JSON AUTO
	RETURN 1
ErrorCode:
	SELECT 
		0 AS STATUS,
		@ErrorMsg AS ErrorMsg
	FROM #TempCurrentAirdropSignInTbl
	FOR JSON AUTO

	RETURN 0

END

GO
