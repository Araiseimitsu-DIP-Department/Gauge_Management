Option Compare Database
Option Explicit

Private Type Gauge
    ID As Long
    Hizuke As Variant
    Kiban As String
    TantouCD As String
    GaugeSize As String
End Type

Public GaugeData As Gauge

Private Type Mast
    sSize As String
    iSuu As Integer
    sCaseNo As String
End Type

Public MastData As Mast