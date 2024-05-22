CREATE VIEW vw_lsd_oi AS
SELECT   i.id id
	,l.id ObsListId
	,i.Species_ID SpeciesId
	,null OtherSpecies
	,i.TagUncertain SpeciesUncertain
	,i.CountMin CountLow
	,i.CountMax CountHigh
	,i.CountExact
	,i.Age_ID Age
	,i.Sex_ID Sex
	,i.Activity_ID Activity
--	,null OtherActivity
	,i.ringmark MarkNo
--	,null MyFirstYear
	,i.Note Note
	,m.id PhotoId
	,i.TagRemarkable IsInteresting
	,i.rarity yIsRare
	,i.commentscount yCommentCount
	,i.lastcommented yLastCommentAdded
--	,null RecOwner
	,i.UpdatedBy_User_ID LastUpdBy
	,i.Created DateCr, i.Updated DateUpd
	,i.Group `Group`
	,lsdi.TimeObs
	,lsdi.LatObs
	,lsdi.LonObs
	,lsdi.LatItem
	,lsdi.LonItem
	,lsdi.GPSAccur
	,lsdi.CountUnit
	,lsdi.Detection
	,lsdi.Territoriality
	,lsdi.FlownOver 
FROM avif.Item i LEFT JOIN avif.List l 
    	ON i.List_ID=l.id LEFT JOIN 
        avif.Media m 
        ON i.id=m.Item_ID RIGHT JOIN
        project.LSD_Item lsdi
        ON lsdi.Item_ID=i.id;
