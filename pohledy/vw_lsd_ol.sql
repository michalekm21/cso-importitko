ALTER VIEW vw_lsd_ol AS
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
	,Author_User_ID ObsOwner
--	,null RecOwner
	,UpdatedBy_User_ID LastUpdBy
	,Created DateCr
	,Updated DateUpd
--	,null DateClosed
--	,null DateDeleted
--	,null ySquareX
--	,null ySquareY
	,Observer
    	,ObserversEmail
FROM avif.List LEFT JOIN avif.View_LSD_Users ON Author_User_ID = ObserverID
WHERE JSON_CONTAINS(Projects, '2', '$');