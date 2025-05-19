<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:v3="urn:hl7-org:v3">
    <xsl:output method="text" indent="no"/>

    <!-- Debug template to print node information -->
    <xsl:template name="debug-node">
        <xsl:param name="node"/>
        <xsl:value-of select="concat('DEBUG: Node name=', name($node), ', Value=', $node)"/>
    </xsl:template>

    <xsl:template match="/">
        <xsl:apply-templates select="v3:document"/>
    </xsl:template>

    <xsl:template match="*">
        <xsl:value-of select="concat('DEBUG: Processing element=', name(), '&#10;')"/>
        <xsl:value-of select="concat('DEBUG: Element namespace=', namespace-uri(), '&#10;')"/>
        <xsl:value-of select="concat('DEBUG: Element attributes=', string-join(for $attr in @* return concat(name($attr), '=', $attr), ', '), '&#10;')"/>
        <xsl:apply-templates select="*"/>
    </xsl:template>

    <xsl:template match="v3:document">
        <xsl:value-of select="concat('DEBUG: Found document element&#10;')"/>
        <xsl:value-of select="concat('DEBUG: Document attributes=', string-join(for $attr in @* return concat(name($attr), '=', $attr), ', '), '&#10;')"/>
        <xsl:value-of select="concat('DEBUG: Number of id elements=', count(v3:id), '&#10;')"/>
        <xsl:value-of select="concat('DEBUG: First id element attributes=', string-join(for $attr in v3:id[1]/@* return concat(name($attr), '=', $attr), ', '), '&#10;')"/>
        <xsl:text>{</xsl:text>
        <xsl:text>"id": "</xsl:text>
        <xsl:value-of select="v3:id/@root"/>
        <xsl:text>"</xsl:text>
        <xsl:text>}</xsl:text>
    </xsl:template>
</xsl:stylesheet>