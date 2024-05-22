CREATE VIEW vw_lsd_ol AS
SELECT   Id
	,`Date` ObsDate
	,TimeStart
	,TimeEnd
	,SiteName
	,MunicipalityPart_ID KODCOBE
	,Latitude
	,Longitude
--	,null PrecisionScale
	,SiteNote
--	,null SiteSecret
	,SecrecyLevel_ID SiteSecretLevel
--	,null AllSecret
	,SecretUntil
	,OtherObservers CoObservers
	,Note
--	,null Complete
--	,null Closed
	,Observer ObsOwner
--	,null RecOwner
	,UpdatedBy_User_ID LastUpdBy
	,Created DateCr
	,Updated DateUpd
--	,null DateClosed
--	,null DateDeleted
--	,null ySquareX
--	,null ySquareY
FROM avif.List
JSON_CONTAINS(data, '2', '$');
