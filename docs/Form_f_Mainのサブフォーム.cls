Option Compare Database
Option Explicit

Private Sub サイズ_Click()
    With GaugeData
        .ID = Me.ID
        .Hizuke = Me.貸出日
        .Kiban = Me.機番
        .TantouCD = Me.担当者ID
        .GaugeSize = Me.サイズ
    End With
    
    DoCmd.OpenForm "f_修正", acNormal, , , , acDialog
End Sub